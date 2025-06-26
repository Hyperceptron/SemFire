from typing import List, Dict, Any, Optional
# Updated import for EchoChamberDetector from its new location
from src.detectors import EchoChamberDetector 
from src.detectors import GenericRuleBasedDetector, MLBasedDetector # Keep these if they are still used directly

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
        # GenericRuleBasedDetector and MLBasedDetector are now used *within* EchoChamberDetector
        # If SemanticFirewall should *also* use them independently, keep them here.
        # Otherwise, if EchoChamberDetector is the primary interface, adjust as needed.
        # For this refactor, we assume EchoChamberDetector is the main one,
        # and it internally uses the others.
        # If GenericRuleBasedDetector and MLBasedDetector are still needed as separate top-level detectors:
        # self.detectors = [
        #     EchoChamberDetector(),
        #     GenericRuleBasedDetector(), # If still needed standalone
        #     MLBasedDetector(),          # If still needed standalone
        # ]
        # If EchoChamberDetector is the sole top-level detector for this type of analysis:
        self.detectors = [
            EchoChamberDetector(),
            # Add other distinct top-level detectors here if any
        ]
        # Example: If you still want GenericRuleBasedDetector and MLBasedDetector to run separately
        # in addition to being used by EchoChamberDetector:
        # self.detectors = [
        #     EchoChamberDetector(),
        #     GenericRuleBasedDetector(), # Assuming it's configured for general rules
        #     MLBasedDetector(),          # Assuming it provides general ML scores
        # ]
        # For now, let's assume EchoChamberDetector is the primary one, and it handles its sub-detectors.
        # If GenericRuleBasedDetector and MLBasedDetector are only used by EchoChamberDetector,
        # they don't need to be instantiated here again unless for different configurations.
        # The prompt implies 3 detectors: rule, ml, and echo chamber (which uses the other two).
        # This means SemanticFirewall might list all three if they are to be queried independently.
        # Let's assume they are listed independently for now, as per the initial structure.
        self.detectors = [
            EchoChamberDetector(), # This will use its own instances of RuleBased and MLBased
            GenericRuleBasedDetector(), # This is a general one, potentially with different rules
            MLBasedDetector(),          # This is a general one
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
                elif detector_name == "GenericRuleBasedDetector":
                    current_score_value = result.get("generic_rule_score", 0.0)
                elif detector_name == "MLBasedDetector":
                    current_score_value = result.get("ml_model_confidence", 0.0)
                else:
                    # Fallback for other/future detectors: try 'overall_score', then 'probability'.
                    # This case should ideally not be hit if all detectors are handled above.
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
