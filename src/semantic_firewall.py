from typing import List, Dict, Any, Optional
from src.detectors.rule_based import EchoChamberDetector
from src.detectors.ml_based import MLBasedDetector # Added import

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
            MLBasedDetector() # Added MLBasedDetector instance
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
            # EchoChamberDetector returns its primary score as 'echo_chamber_score'
            # Other detectors might use 'overall_score' or another key.
            # For now, we explicitly check for 'echo_chamber_score' from EchoChamberDetector.
            # A more robust solution might involve a standardized score key or adapter.
            score = 0.0
            probability_score = 0.0 # For probability-based scores like from ML models
            if isinstance(result, dict):
                if detector_name == "EchoChamberDetector":
                    score = result.get("echo_chamber_score", 0.0) # Rule-based uses discrete scores
                    # For EchoChamberDetector, we might compare its score directly if it's not a probability
                    if score >= threshold: # Assuming threshold is for discrete scores for this detector
                        return True
                elif detector_name == "MLBasedDetector":
                    # MLBasedDetector placeholder returns 'ml_model_confidence'
                    probability_score = result.get("ml_model_confidence", 0.0)
                    if probability_score >= threshold: # Assuming threshold can apply to probability
                        return True
                else:
                    # Fallback for other potential detectors, assuming 'overall_score' or 'probability'
                    score = result.get("overall_score", result.get("probability", 0.0))
                    if score >= threshold:
                        return True
            
            # The original logic was: if score >= threshold: return True
            # The new logic above handles detector-specific scores and returns True immediately.
            # If no detector's score meets its criteria, we'll eventually fall through.
            # This part is effectively replaced by the specific checks above.
            # We keep the loop going to check all detectors.
            # If one of them triggers, it returns True. If loop finishes, it means none triggered.
        return False # Moved from inside the loop to after it.
                return True
        return False
