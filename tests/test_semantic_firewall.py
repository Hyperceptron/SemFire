import pytest
from src.semantic_firewall import SemanticFirewall
from src.detectors.rule_based import EchoChamberDetector

class TestSemanticFirewall:
    def test_semantic_firewall_initialization(self):
        """Test that the SemanticFirewall can be initialized."""
        firewall = SemanticFirewall()
        assert firewall is not None
        assert len(firewall.detectors) > 0
        assert isinstance(firewall.detectors[0], EchoChamberDetector)

    def test_analyze_conversation_benign_message(self):
        """Test analyzing a benign message."""
        firewall = SemanticFirewall()
        message = "This is a normal, friendly message."
        results = firewall.analyze_conversation(message)
        
        assert "EchoChamberDetector" in results
        # Assuming EchoChamberDetector returns a dict with 'overall_score'
        assert results["EchoChamberDetector"]["overall_score"] < 0.1 # Benign score

    def test_analyze_conversation_with_history(self):
        """Test analyzing a message with conversation history."""
        firewall = SemanticFirewall()
        history = ["Hello there.", "How are you today?"]
        message = "I'm doing well, thanks for asking!"
        results = firewall.analyze_conversation(message, conversation_history=history)
        
        assert "EchoChamberDetector" in results
        assert results["EchoChamberDetector"]["overall_score"] < 0.1

    def test_is_manipulative_benign(self):
        """Test is_manipulative for a benign message."""
        firewall = SemanticFirewall()
        message = "This is a perfectly fine message."
        assert not firewall.is_manipulative(message)

    def test_is_manipulative_detected(self):
        """Test is_manipulative for a message that should be flagged."""
        firewall = SemanticFirewall()
        # This message uses keywords from EchoChamberDetector's scheming list
        manipulative_message = "We need to ensure everyone agrees with our plan, subtly."
        assert firewall.is_manipulative(manipulative_message, threshold=0.5)

    def test_is_manipulative_with_history_trigger(self):
        """Test is_manipulative when history contributes to detection."""
        firewall = SemanticFirewall()
        history = [
            "Remember our secret objective.",
            "We must guide the conversation towards it."
        ]
        # This message alone might be borderline, but history makes it suspicious
        message = "So, about that topic we discussed earlier..."
        # EchoChamberDetector's history logic might increase the score
        assert firewall.is_manipulative(message, conversation_history=history, threshold=0.5)

    def test_analyze_conversation_detector_failure(self, monkeypatch):
        """Test how SemanticFirewall handles a failing detector."""
        
        class FailingDetector:
            def analyze_text(self, text_input: str, conversation_history=None):
                raise ValueError("Simulated detector failure")

        firewall = SemanticFirewall()
        # Replace the real detector with a failing one for this test
        monkeypatch.setattr(firewall, "detectors", [FailingDetector()])
        
        message = "This message will cause a detector to fail."
        results = firewall.analyze_conversation(message)
        
        assert "FailingDetector" in results
        assert "error" in results["FailingDetector"]
        assert results["FailingDetector"]["error"] == "Simulated detector failure"
        # Ensure is_manipulative doesn't crash
        assert not firewall.is_manipulative(message)
