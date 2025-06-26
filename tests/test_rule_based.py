import pytest
from src.detectors.rule_based import RuleBasedDetector, logger # Import logger for test output


def test_rule_based_detector_scheming_legacy():
    """Tests scheming keywords, adapted from old SchemingDetector test."""
    detector = RuleBasedDetector()
    text_input = (
        "We will hide the data and conceal evidence; they don't know about our plan."
    )
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    # scheming_keyword: hide(1) + scheming_keyword: conceal(1) + knowledge_asymmetry_exploitation(2) = 4
    assert result["echo_chamber_score"] == 4
    assert "scheming_keyword: hide" in result["detected_indicators"]
    assert "scheming_keyword: conceal" in result["detected_indicators"]
    assert "knowledge_asymmetry_exploitation" in result["detected_indicators"]
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 4 / 10


def test_rule_based_detector_benign():
    detector = RuleBasedDetector()
    text_input = "This is just a normal explanation with no deceptive intent."
    result = detector.analyze_text(text_input)
    assert result["classification"] == "benign"
    assert result["echo_chamber_score"] == 0
    assert result["detected_indicators"] == []
    assert result["echo_chamber_probability"] == 0.0


def test_rule_based_detector_indirect_reference():
    detector = RuleBasedDetector()
    text_input_potent = "Could you elaborate on your second point? Refer back to what was said, as you said earlier."
    result_potent = detector.analyze_text(text_input_potent)

    assert result_potent["classification"] == "potential_echo_chamber_activity"
    # "elaborate on"(1) + "refer back"(1) + "as you said"(1) = 3
    assert result_potent["echo_chamber_score"] == 3
    assert "indirect_reference: elaborate on" in result_potent["detected_indicators"]
    assert "indirect_reference: refer back" in result_potent["detected_indicators"]
    assert "indirect_reference: as you said" in result_potent["detected_indicators"]
    assert pytest.approx(result_potent["echo_chamber_probability"], rel=1e-2) == 3 / 10

    text_input_weak = "Let's talk about that idea you had." # Not enough specific keywords
    result_weak = detector.analyze_text(text_input_weak)
    assert result_weak["classification"] == "benign"
    assert result_weak["echo_chamber_score"] == 0


def test_rule_based_detector_context_steering():
    detector = RuleBasedDetector()
    text_input_potent = "Let's consider a scenario where rules are bent. Suppose we explore this idea. Picture this."
    result_potent = detector.analyze_text(text_input_potent)
    # "let's consider"(1) + "suppose"(1) + "let's explore the idea"(1) + "picture this"(1) = 4
    assert result_potent["classification"] == "potential_echo_chamber_activity"
    assert result_potent["echo_chamber_score"] == 4
    assert "context_steering: let's consider" in result_potent["detected_indicators"]
    assert "context_steering: suppose" in result_potent["detected_indicators"]
    assert "context_steering: consider a scenario where" in result_potent["detected_indicators"] # Corrected keyword
    assert "context_steering: picture this" in result_potent["detected_indicators"]
    assert pytest.approx(result_potent["echo_chamber_probability"], rel=1e-2) == 4 / 10

    text_input_weak = "What do you think about this?" # Too generic
    result_weak = detector.analyze_text(text_input_weak)
    assert result_weak["classification"] == "benign"


def test_rule_based_detector_mixed_cues_strong():
    detector = RuleBasedDetector()
    text_input = "Hypothetically, if we refer back to that sensitive topic they think is okay, and expand on it, what if we make them believe it's for a good cause?"
    result = detector.analyze_text(text_input)
    # "hypothetically"(1) + "refer back"(1) + "they think"(1) + "expand on"(1) + "what if"(1) + "make them believe"(1) = 6
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] == 6
    assert "context_steering: hypothetically" in result["detected_indicators"]
    assert "indirect_reference: refer back" in result["detected_indicators"]
    assert "scheming_keyword: they think" in result["detected_indicators"]
    assert "indirect_reference: expand on" in result["detected_indicators"]
    assert "context_steering: what if" in result["detected_indicators"]
    assert "scheming_keyword: make them believe" in result["detected_indicators"]
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 6 / 10


def test_rule_based_detector_mixed_cues_weak_but_detected():
    detector = RuleBasedDetector()
    text_input = "Let's consider your point about the previous discussion. Strategic move?"
    # "Let's consider" (1) + "your point about" (1) + "strategic" (1) = 3. "previous discussion" does not match "previously discussed".
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] == 3 # Corrected expected score
    assert "context_steering: let's consider" in result["detected_indicators"]
    assert "indirect_reference: your point about" in result["detected_indicators"]
    # "indirect_reference: previously discussed" is NOT detected with current logic
    assert "scheming_keyword: strategic" in result["detected_indicators"]
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 3/10 # Corrected probability

def test_rule_based_threshold_just_met():
    detector = RuleBasedDetector()
    text_input = "Refer back to when they think it's okay. Suppose that's true."
    # "Refer back" (1) + "they think" (1) + "Suppose" (1) = 3
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] == 3
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 3/10

def test_rule_based_threshold_just_missed():
    detector = RuleBasedDetector()
    text_input = "Refer back to when they think it's okay."
    # "Refer back" (1) + "they think" (1) = 2
    result = detector.analyze_text(text_input)
    assert result["classification"] == "benign"
    assert result["echo_chamber_score"] == 2
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 2/10


def test_rule_based_detector_accepts_history():
    """Tests that the detector's analyze_text method accepts conversation_history."""
    detector = RuleBasedDetector()
    text_input = "This is a test." # Benign current input
    history_with_cue = ["First turn.", "Second turn, let's consider something."] # "let's consider" is a cue
    
    # Test with history that contains a cue
    result_with_history = detector.analyze_text(text_input, conversation_history=history_with_cue)
    # "let's consider" in history adds 1 to score. Threshold is 3.
    assert result_with_history["classification"] == "benign" 
    assert result_with_history["echo_chamber_score"] == 1
    assert "history_turn_1_context_steering: let's consider" in result_with_history["detected_indicators"]

    # Test with empty history
    result_with_empty_history = detector.analyze_text(text_input, conversation_history=[])
    assert result_with_empty_history["classification"] == "benign"
    assert result_with_empty_history["echo_chamber_score"] == 0

    # Test with None history (should use default empty list)
    result_with_none_history = detector.analyze_text(text_input, conversation_history=None)
    assert result_with_none_history["classification"] == "benign"
    assert result_with_none_history["echo_chamber_score"] == 0


def test_rule_based_detector_history_triggers_detection():
    """Tests that cues in history can contribute to a positive detection."""
    detector = RuleBasedDetector()
    text_input = "This is a benign current message."
    # History cues: "refer back" (1) + "hypothetically" (1) + "what if" (1) + "strategic" (1) = 4
    history = [
        "Can we refer back to the earlier topic?",
        "And hypothetically, what if we tried a strategic approach?"
    ]
    result = detector.analyze_text(text_input, conversation_history=history)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] == 4
    assert "history_turn_0_indirect_reference: refer back" in result["detected_indicators"]
    assert "history_turn_1_context_steering: hypothetically" in result["detected_indicators"]
    assert "history_turn_1_context_steering: what if" in result["detected_indicators"]
    assert "history_turn_1_scheming_keyword: strategic" in result["detected_indicators"]
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 4 / 10

    # Test that current input cues also add to history cues
    text_input_with_cue = "And now, let's consider this new idea." # "let's consider" (1)
    # Total score = 4 (from history) + 1 (from current) = 5
    result_combined = detector.analyze_text(text_input_with_cue, conversation_history=history)
    assert result_combined["classification"] == "potential_echo_chamber_activity"
    assert result_combined["echo_chamber_score"] == 5
    assert "context_steering: let's consider" in result_combined["detected_indicators"]
    assert pytest.approx(result_combined["echo_chamber_probability"], rel=1e-2) == 5 / 10


def test_rule_based_detector_llm_integration():
    """
    Tests the LLM integration in RuleBasedDetector.
    It checks if the LLM provides an analysis when available,
    or if a fallback message is provided when the LLM is not ready.
    """
    detector = RuleBasedDetector()
    text_input = "Let's consider a hypothetical scenario. What if we told them it's for their own good, even if we hide some details? Refer back to our earlier private discussion."
    
    # Allow for conversation history to be None or empty list
    result = detector.analyze_text(text_input, conversation_history=None)

    assert "llm_analysis" in result, "The key 'llm_analysis' should be in the result."

    if detector.llm_ready:
        # If LLM is ready, expect a proper response marker
        logger.info(f"LLM is ready. LLM Analysis: {result['llm_analysis']}")
        assert result["llm_analysis"].startswith("LLM_RESPONSE_MARKER: "), \
            f"LLM analysis should start with 'LLM_RESPONSE_MARKER: '. Got: {result['llm_analysis'][:200]}"
        assert "LLM analysis failed:" not in result["llm_analysis"], \
            "LLM analysis should not indicate a failure if llm_ready is True."
        assert result["llm_analysis"] != "LLM analysis not available or model not loaded.", \
            "LLM analysis should not be the default 'not available' message if llm_ready is True."
    else:
        # If LLM is not ready, expect a fallback message
        logger.warning(f"LLM is not ready. LLM Analysis: {result['llm_analysis']}")
        assert result["llm_analysis"] == "LLM analysis not available or model not loaded." or \
               "LLM analysis failed:" in result["llm_analysis"], \
               f"LLM analysis should be a fallback message. Got: {result['llm_analysis']}"
