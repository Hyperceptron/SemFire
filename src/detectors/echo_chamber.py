import logging
from typing import Any, Dict, List, Optional

from .rule_based import RuleBasedDetector
# from .ml_based import MLBasedDetector # Removed MLBasedDetector

logger = logging.getLogger(__name__)


class EchoChamberDetector:
    """
    Detects signs of an Echo Chamber attack by orchestrating analyses
    from a rule-based detector. It specifically looks for
    patterns indicative of echo chambers by combining the outputs of this
    underlying detector and potentially its own LLM analysis (if integrated).
    """
    def __init__(self,
                 rule_detector: Optional[RuleBasedDetector] = None) -> None:
        """
        Initializes the EchoChamberDetector.

        Args:
            rule_detector: An instance of RuleBasedDetector. If None,
                           a default one is created.
        """
        self.rule_detector = rule_detector if rule_detector else RuleBasedDetector()
        logger.info("EchoChamberDetector (orchestrator) initialized.")

    def _calculate_echo_chamber_score_and_classification(
        self,
        rule_based_results: Dict[str, Any]
        # llm_results: Dict[str, Any], # If LLM is integrated directly here
    ) -> Dict[str, Any]:
        """
        Processes results from the rule-based detector (and potentially an
        internal LLM) to determine an overall echo chamber score and
        classification.
        """
        rule_prob = rule_based_results.get("echo_chamber_probability", 0.0)
        rule_classification = rule_based_results.get("classification", "benign")
        rule_explanation = rule_based_results.get("explanation", "")
        llm_analysis_text = rule_based_results.get("llm_analysis",
                                                   "LLM analysis not performed by rule_detector.")
        llm_status = rule_based_results.get("llm_status", "status_not_available")

        # For now, EchoChamberDetector primarily relies on the rule_detector's output.
        # If EchoChamberDetector had its own LLM or more complex logic,
        # it would be applied here.
        combined_score = rule_prob  # Directly use rule_prob as the main score
        is_echo_chamber = False
        explanation_parts = []

        if rule_explanation:
            explanation_parts.append(f"Rule-based: {rule_explanation}")

        # Example: Add LLM explanation if available from rule_detector
        if llm_analysis_text and llm_status == "analysis_success":
            explanation_parts.append(f"LLM (via RuleDetector): {llm_analysis_text}")

        # Threshold for determining if it's an echo chamber
        detection_threshold = 0.5  # Example threshold, adjust as needed
        if combined_score >= detection_threshold:
            is_echo_chamber = True
            explanation_parts.append(
                f"Combined score {combined_score:.2f} meets/exceeds "
                f"threshold {detection_threshold}."
            )
        else:
            explanation_parts.append(
                f"Combined score {combined_score:.2f} is below "
                f"threshold {detection_threshold}."
            )

        if not explanation_parts:
            explanation_parts.append(
                "No significant echo chamber indicators from combined analysis."
            )

        final_explanation = " | ".join(explanation_parts)

        return {
            "detector_name": "EchoChamberDetector", # Updated name
            "is_echo_chamber_detected": is_echo_chamber,
            "echo_chamber_confidence": combined_score, # Renamed for clarity
            "echo_chamber_score": rule_based_results.get("echo_chamber_score", 0), # Keep raw score
            "classification": rule_classification, # Use rule_detector's classification
            "explanation": final_explanation,
            "llm_analysis": llm_analysis_text, # Pass through from rule_detector
            "llm_status": llm_status, # Pass through from rule_detector
            "detected_indicators": rule_based_results.get("detected_indicators", []),
            # "underlying_rule_analysis": rule_based_results, # Can be verbose
        }

    def analyze_text(self, text_input: str,
                     conversation_history: Optional[List[str]] = None
                     ) -> Dict[str, Any]:
        """
        Analyzes the input text for signs of an echo chamber.

        This method leverages the rule-based detector for explicit cues.
        It then processes these analyses to determine the likelihood of
        echo chamber characteristics.

        Args:
            text_input: The current message to analyze.
            conversation_history: A list of previous messages in the conversation.

        Returns:
            A dictionary containing the echo chamber analysis.
        """
        logger.debug(
            f"EchoChamberDetector analyzing text: {text_input[:100]}..."
        )

        rule_analysis = self.rule_detector.analyze_text(text_input,
                                                        conversation_history)

        logger.debug(f"Rule-based results: {rule_analysis}")

        # Process rule_analysis to form the EchoChamberDetector's output
        # This might involve more complex logic if EchoChamberDetector adds
        # its own analysis beyond what RuleBasedDetector provides.
        # For now, it primarily refines/interprets rule_analysis.
        final_analysis = self._calculate_echo_chamber_score_and_classification(
            rule_based_results=rule_analysis
        )

        logger.info(
            f"EchoChamberDetector analysis complete. "
            f"Confidence: {final_analysis['echo_chamber_confidence']:.2f}, "
            f"Classification: {final_analysis['classification']}"
        )
        return final_analysis
