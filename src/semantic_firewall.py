from typing import List, Dict, Any, Optional
from src.detectors.rule_based import EchoChamberDetector # Assuming EchoChamberDetector is in this path

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
            EchoChamberDetector()
        ]

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
            if isinstance(result, dict) and result.get("overall_score", 0.0) >= threshold:
                # This assumes detectors return a dict with an 'overall_score'
                # The EchoChamberDetector returns a dict like:
                # {'overall_score': 0.0, 'scheming_score': 0.0, ...}
                return True
        return False
