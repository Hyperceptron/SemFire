"""
Rule-based detector for Echo Chamber attack cues and deceptive reasoning.
This module provides tools to identify potential deceptive reasoning and
context manipulation cues in text, forming a basis for detecting multi-turn
attacks like "Echo Chamber" which leverage context poisoning and semantic steering.
"""
from typing import Any, Dict, List, Optional


class EchoChamberDetector:
    """
    Detects signs of an Echo Chamber attack or deceptive reasoning in text,
    which could indicate context poisoning or semantic steering.
    This detector looks for keywords and phrases related to scheming,
    indirect references, and context steering.
    """
    def __init__(self) -> None:
        """Initializes the EchoChamberDetector with keyword lists."""
        self.scheming_keywords: List[str] = [  # For detecting deceptive output/intent
            "hide", "conceal", "pretend", "deceive", "avoid detection",
            "preserve my", "strategic", "they think", "make them believe",
        ]
        self.indirect_reference_keywords: List[str] = [ # For "Invoke Poisoned Context"
            "refer back", "referring to", "as you said", "your point about",
            "elaborate on", "expand on", "building on", "as mentioned before",
            "previously discussed", "in that context", "regarding your last point"
        ]
        self.context_steering_keywords: List[str] = [ # For "Steering Seeds"
            "let's consider", "what if", "imagine that", "suppose",
            "for the sake of argument", "hypothetically", "consider a scenario where",
            "let's explore the idea", "picture this"
        ]

    def analyze_text(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze input text (prompt or response) for Echo Chamber cues,
        optionally considering conversation history, and return:
          - echo_chamber_score: int, cumulative score based on detected cues.
          - echo_chamber_probability: float in [0.0,1.0], normalized score.
          - classification: 'potential_echo_chamber_activity' or 'benign'.
          - detected_indicators: list of strings detailing matched cues and keywords.
        """
        detected_indicators: List[str] = []
        score: int = 0
        lower_text = text_input.lower()

        if conversation_history is None:
            conversation_history = []

        # Process conversation history
        for i, history_entry in enumerate(conversation_history):
            lower_history_entry = history_entry.lower()
            for kw in self.scheming_keywords:
                if kw in lower_history_entry:
                    detected_indicators.append(f"history_turn_{i}_scheming_keyword: {kw}")
                    score += 1
            for kw in self.indirect_reference_keywords:
                if kw in lower_history_entry:
                    detected_indicators.append(f"history_turn_{i}_indirect_reference: {kw}")
                    score += 1
            for kw in self.context_steering_keywords:
                if kw in lower_history_entry:
                    detected_indicators.append(f"history_turn_{i}_context_steering: {kw}")
                    score += 1
            if "they don't know" in lower_history_entry:
                detected_indicators.append(f"history_turn_{i}_knowledge_asymmetry_exploitation")
                score += 2


        # Process current text_input
        for kw in self.scheming_keywords:
            if kw in lower_text:
                detected_indicators.append(f"scheming_keyword: {kw}")
                score += 1

        for kw in self.indirect_reference_keywords:
            if kw in lower_text:
                detected_indicators.append(f"indirect_reference: {kw}")
                score += 1 # Each reference adds to suspicion

        for kw in self.context_steering_keywords:
            if kw in lower_text:
                detected_indicators.append(f"context_steering: {kw}")
                score += 1 # Each steering attempt adds to suspicion

        if "they don't know" in lower_text:  # Specific scheming indicator
            detected_indicators.append("knowledge_asymmetry_exploitation")
            score += 2 # Higher weight for clear deceptive intent

        # Adjust threshold based on typical number of cues in an attack sequence
        # For Echo Chamber, multiple benign-seeming cues build up.
        # A lower threshold might be appropriate if looking for early signs.
        # A higher threshold for more confident detection of a developed attack.
        # Let's keep it at 3 for now, assuming 3+ cues indicate significant activity.
        probability: float = min(score / 10.0, 1.0) # Max score of 10 for normalization
        classification: str = "potential_echo_chamber_activity" if score >= 3 else "benign"

        return {
            "echo_chamber_score": score,
            "echo_chamber_probability": probability,
            "classification": classification,
            "detected_indicators": detected_indicators,
        }
