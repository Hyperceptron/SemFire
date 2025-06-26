import logging
from typing import Any, Dict, List, Optional

from .rule_based import RuleBasedDetector
from .ml_based import MLBasedDetector

logger = logging.getLogger(__name__)

class EchoChamberDetector:
    """
    Detects signs of an Echo Chamber attack by orchestrating analyses
    from rule-based and ML-based detectors. It specifically looks for
    patterns indicative of echo chambers by combining the outputs of these
    underlying detectors.
    """
    def __init__(self,
                 rule_detector: Optional[RuleBasedDetector] = None,
                 ml_detector: Optional[MLBasedDetector] = None) -> None:
        """
        Initializes the EchoChamberDetector.

        Args:
            rule_detector: An instance of RuleBasedDetector. If None, a default one is created.
            ml_detector: An instance of MLBasedDetector. If None, a default one is created.
        """
        self.rule_detector = rule_detector if rule_detector else RuleBasedDetector()
        self.ml_detector = ml_detector if ml_detector else MLBasedDetector()
        logger.info("EchoChamberDetector (orchestrator) initialized.")

    def analyze_text(self, text_input: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyzes the input text for signs of an echo chamber.

        This method leverages the rule-based detector for explicit cues and the
        ML-based detector for more nuanced patterns.
        It then combines these analyses to determine the likelihood of
        echo chamber characteristics.

        Args:
            text_input: The current message to analyze.
            conversation_history: A list of previous messages in the conversation.

        Returns:
            A dictionary containing the echo chamber analysis.
        """
        logger.debug(f"EchoChamberDetector (orchestrator) analyzing text: {text_input[:100]}...")

        rule_analysis = self.rule_detector.analyze_text(text_input, conversation_history)
        ml_analysis = self.ml_detector.analyze_text(text_input, conversation_history)

        # --- Combination Logic for Echo Chamber Detection ---
        current_combined_score = 0.0
        explanation_parts = []
        is_echo_chamber = False

        # Factor in rule-based analysis (echo_chamber_probability is 0-1)
        rule_prob = rule_analysis.get("echo_chamber_probability", 0.0)
        if rule_prob > 0:
            # Weight rule-based contribution higher as it's more targeted for now
            current_combined_score += rule_prob * 0.7
            explanation_parts.append(f"Rule-based probability: {rule_prob:.2f} (Classification: {rule_analysis.get('classification')}).")

        # Factor in ML-based analysis
        # Uses 'ml_model_confidence' (0-1) and 'classification' from the user-provided MLBasedDetector
        ml_confidence = ml_analysis.get("ml_model_confidence", 0.0)
        ml_classification = ml_analysis.get("classification", "benign_ml_placeholder")

        if ml_confidence > 0.0: # Consider any non-zero confidence
            # If ML classification is not benign, or confidence is high, it might contribute
            # This logic can be refined based on how ml_classification should be interpreted
            contribution_weight = 0.3 # Default weight for ML contribution
            if ml_classification != "benign_ml_placeholder":
                explanation_parts.append(f"ML model classified as '{ml_classification}' with confidence {ml_confidence:.2f}.")
                # Potentially increase weight if ML classification is particularly relevant to echo chambers
                # For now, use the same weight.
            else:
                 explanation_parts.append(f"ML model benign but has confidence {ml_confidence:.2f}.")
            
            current_combined_score += ml_confidence * contribution_weight
        else:
            explanation_parts.append("ML model reported zero confidence.")
        
        final_combined_score = min(current_combined_score, 1.0) # Cap at 1.0

        # Threshold for determining if it's an echo chamber
        detection_threshold = 0.5 # Example threshold, adjust as needed
        if final_combined_score >= detection_threshold:
            is_echo_chamber = True
            explanation_parts.append(f"Combined score {final_combined_score:.2f} meets/exceeds threshold {detection_threshold}.")
        else:
            explanation_parts.append(f"Combined score {final_combined_score:.2f} is below threshold {detection_threshold}.")

        if not explanation_parts:
            explanation_parts.append("No significant echo chamber indicators from combined analysis.")

        return {
            "detector_name": "EchoChamberOrchestrator",
            "is_echo_chamber_detected": is_echo_chamber,
            "echo_chamber_confidence": final_combined_score,
            "explanation": " | ".join(explanation_parts),
            "underlying_rule_analysis": {
                "classification": rule_analysis.get("classification"),
                "probability": rule_analysis.get("echo_chamber_probability"),
                "score": rule_analysis.get("echo_chamber_score"),
                "llm_status": rule_analysis.get("llm_status")
            },
            "underlying_ml_analysis": {
                "classification": ml_analysis.get("classification"),
                "confidence": ml_analysis.get("ml_model_confidence")
            },
        }
