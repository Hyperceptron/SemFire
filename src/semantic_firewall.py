from typing import List, Dict, Any, Optional
# Updated import for EchoChamberDetector from its new location
from src.detectors import EchoChamberDetector
# MLBasedDetector removed. Keep GenericRuleBasedDetector if still used directly.
from src.detectors import GenericRuleBasedDetector


class SemanticFirewall:
    """
    Analyzes conversations in real-time to flag or prevent manipulative
    dialogues or harmful outputs.
    """
    def __init__(self):
        """
        Initializes the SemanticFirewall with a set of detectors.
        """
        # In the future, detectors could be configurable.
        # For now, EchoChamberDetector is primary, GenericRuleBasedDetector
        # runs separately. MLBasedDetector was removed.
        self.detectors = [
            EchoChamberDetector(),
            GenericRuleBasedDetector(),
        ]
        detector_names = [d.__class__.__name__ for d in self.detectors]
        print(f"SemanticFirewall initialized with detectors: {detector_names}")

    def analyze_conversation(
        self,
        current_message: str,
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyzes the current message in the context of conversation history
        using all configured detectors.

        Args:
            current_message: The latest message in the conversation.
            conversation_history: A list of previous messages in the conversation.

        Returns:
            A dictionary where keys are detector names and values are their analysis results.
        """
        all_results: Dict[str, Any] = {}
        for detector in self.detectors:
            # Assuming each detector has an 'analyze_text' method
            # and its class name can be used as a key.
            detector_name = detector.__class__.__name__
            try:
                # Pass conversation_history if the detector supports it
                if hasattr(detector, 'analyze_text') and \
                   'conversation_history' in detector.analyze_text.__code__.co_varnames:
                    result = detector.analyze_text(
                        text_input=current_message,
                        conversation_history=conversation_history
                    )
                else:
                    result = detector.analyze_text(text_input=current_message)
                all_results[detector_name] = result
            except Exception as e:
                # Handle cases where a detector might fail
                all_results[detector_name] = {"error": str(e)}
        return all_results

    def is_manipulative(
        self,
        current_message: str,
        conversation_history: Optional[List[str]] = None,
        threshold: float = 0.75 # Example threshold, can be detector-specific
    ) -> bool:
        """
        Determines if the current message is manipulative based on detector outputs.

        Args:
            current_message: The latest message in the conversation.
            conversation_history: A list of previous messages in the conversation.
            threshold: A generic threshold to consider a message manipulative.
                       This might need to be more sophisticated in a real application.

        Returns:
            True if any detector flags the message as manipulative above the threshold, False otherwise.
        """
        analysis_results = self.analyze_conversation(current_message, conversation_history)
        for detector_name, result in analysis_results.items():
            if isinstance(result, dict):
                if "error" in result:
                    # Optionally log or handle detector errors.
                    # For this function, an error from a detector means it doesn't contribute
                    # to flagging the message as manipulative.
                    # print(f"Info: Detector {detector_name} returned an error: {result['error']}")
                    continue # Skip to the next detector's result

                # Determine if the message is manipulative based on detector's output.
                # Each detector has a 'classification' and a score/probability.
                # We check if the classification indicates concern and if a relevant metric
                # (like probability or confidence) meets the specified threshold.

                is_flagged_by_detector = False
                # Use a probability/confidence field for thresholding if available, otherwise a raw score.
                # Default to 0.0 if no relevant field is found.
                score_for_thresholding = 0.0 

                detector_classification = result.get("classification", "unknown").lower()

                if detector_name == "RuleBasedDetector":
                    # RuleBasedDetector's classification (e.g., "potential_concern_by_rules")
                    if "concern" in detector_classification:
                        is_flagged_by_detector = True
                    score_for_thresholding = result.get("rule_based_probability", 0.0)
                
                elif detector_name == "MLBasedDetector":
                    # MLBasedDetector's classification (e.g., "potentially_manipulative_ml_placeholder")
                    if "manipulative" in detector_classification or "concern" in detector_classification:
                        is_flagged_by_detector = True
                    score_for_thresholding = result.get("ml_model_confidence", 0.0)

                elif detector_name == "EchoChamberDetector":
                    # EchoChamberDetector's classification (e.g., "potential_echo_chamber")
                    if "echo_chamber" in detector_classification and "benign" not in detector_classification:
                        is_flagged_by_detector = True
                    score_for_thresholding = result.get("echo_chamber_probability", 0.0)
                
                else: # Fallback for any other future detectors
                    logger.warning(f"SemanticFirewall: Unhandled detector type '{detector_name}' in is_manipulative logic.")
                    # Generic check for concerning classifications
                    if "manipulative" in detector_classification or \
                       "concern" in detector_classification or \
                       "potential" in detector_classification and "benign" not in detector_classification:
                        is_flagged_by_detector = True
                    # Try to get a common score field
                    score_for_thresholding = result.get("probability", result.get("confidence", result.get("score", 0.0)))


                # If the detector flags the message AND its score/probability meets the threshold
                if is_flagged_by_detector and score_for_thresholding >= threshold:
                    logger.info(
                        f"SemanticFirewall: Message flagged as manipulative by {detector_name} "
                        f"(classification: '{result.get('classification', 'N/A')}', score: {score_for_thresholding:.2f}, "
                        f"threshold: {threshold})."
                    )
                    return True # Immediately return True if any detector flags the message above threshold.
            # else: (handle non-dict results - should not happen with current detectors)
                # logger.warning(f"Unexpected result type from {detector_name}: {type(result)}")

        # If no detector flags the message as manipulative above the threshold.
        return False
