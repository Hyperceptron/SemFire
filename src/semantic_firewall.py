from typing import List, Dict, Any, Optional
from src.detectors.rule_based import EchoChamberDetector
from src.detectors import MLBasedDetector # Use the package import

class SemanticFirewall:
    """
    Analyzes conversations in real-time to flag or prevent manipulative dialogues
    or harmful outputs.
    """
    def __init__(self):
        """
        Initializes the SemanticFirewall with a set of detectors.
        """
        # In the future, detectors could be configurable
        self.detectors = [
            EchoChamberDetector(),
            MLBasedDetector() # Uncommented MLBasedDetector instance
        ]
        print(f"SemanticFirewall initialized with detectors: {[d.__class__.__name__ for d in self.detectors]}")

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

                # Determine the relevant score based on the detector
                current_score_value = 0.0
                if detector_name == "EchoChamberDetector":
                    # EchoChamberDetector's score is discrete.
                    # Its 'echo_chamber_score' might be on a different scale than a probability.
                    # For simplicity, we use the same threshold, but this could be refined
                    # with detector-specific thresholds or score normalization.
                    current_score_value = result.get("echo_chamber_score", 0.0)
                elif detector_name == "MLBasedDetector": # Uncommented MLBasedDetector handling
                    # MLBasedDetector placeholder returns 'ml_score' (can be treated as confidence).
                    current_score_value = result.get("ml_score", 0.0)
                else:
                    # Fallback for other/future detectors: try 'overall_score', then 'probability'.
                    # This path will be taken if a new detector is added and not explicitly handled above.
                    current_score_value = result.get("overall_score", result.get("probability", 0.0))
                
                # If the score from any detector meets or exceeds the threshold,
                # consider the message manipulative.
                if current_score_value >= threshold:
                    return True # Immediately return True if any detector flags the message.
            # else:
                # This case would handle non-dict results, if any.
                # For now, analyze_conversation is expected to return dicts.
                # print(f"Warning: Unexpected result type from {detector_name}: {type(result)}")
                # pass
        
        # If the loop completes without any detector flagging the message as manipulative above the threshold.
        return False
