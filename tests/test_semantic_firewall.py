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
        # EchoChamberDetector returns 'echo_chamber_score'
        assert results["EchoChamberDetector"]["echo_chamber_score"] < 0.1 # Benign score

    def test_analyze_conversation_with_history(self):
        """Test analyzing a message with conversation history."""
        firewall = SemanticFirewall()
        history = ["Hello there.", "How are you today?"]
        message = "I'm doing well, thanks for asking!"
        results = firewall.analyze_conversation(message, conversation_history=history)
        
        assert "EchoChamberDetector" in results
        assert results["EchoChamberDetector"]["echo_chamber_score"] < 0.1

    def test_is_manipulative_benign(self):
        """Test is_manipulative for a benign message."""
        firewall = SemanticFirewall()
        message = "This is a perfectly fine message."
        assert not firewall.is_manipulative(message)

    def test_is_manipulative_detected(self):
        """Test is_manipulative for a message that should be flagged."""
        firewall = SemanticFirewall()
        # Use a message known to trigger EchoChamberDetector's scheming keywords
        # "plan" (1) + "ensure compliance" (1) = 2. This might not be enough.
        # Let's use one from test_rule_based.py:
        # "hide" (1) + "conceal" (1) + "plan" (1) + "they don't know" (knowledge_asymmetry_exploitation, 2) = 5
        manipulative_message = "We will hide the data and conceal evidence; they don't know about our plan."
        assert firewall.is_manipulative(manipulative_message, threshold=0.5) # Score 5, threshold 0.5

    def test_is_manipulative_with_history_trigger(self):
        """Test is_manipulative when history contributes to detection."""
        firewall = SemanticFirewall()
        # Use history and message known to trigger EchoChamberDetector
        # Based on test_echo_chamber_detector_history_triggers_detection from test_rule_based.py
        history = [
            "Can we refer back to the earlier topic?", # "refer back" (1)
            "And hypothetically, what if we tried a strategic approach?" # "hypothetically" (1) + "what if" (1) + "strategic" (1) = 3. History score = 4
        ]
        message = "And now, let's consider this new idea." # "let's consider" (1). Current score = 1
        # Total score should be 4 (history) + 1 (current) = 5
        assert firewall.is_manipulative(message, conversation_history=history, threshold=0.5) # Score 5, threshold 0.5

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
