import pytest
from src.detectors.echo_chamber_detector import EchoChamberDetector, logger # Import logger for test output
# Note: The import above is changed from rule_based to echo_chamber_detector

# TODO: These tests will likely need adjustments:
# 1. Mocking for RuleBasedDetector and MLBasedDetector if their interaction is complex.
# 2. Mocking for LLM loading in EchoChamberDetector's __init__ to avoid actual model download/load during tests.
# 3. Verification of "detected_indicators" format, as it now combines outputs and might have new prefixes.
#    The new RuleBasedDetector outputs "source_category_keyword: kw".
#    The EchoChamberDetector's _calculate_echo_chamber_score_and_classification now handles "knowledge_asymmetry_exploitation".

def test_echo_chamber_detector_scheming_legacy():
    """Tests scheming keywords, adapted from old SchemingDetector test."""
    detector = EchoChamberDetector() # This will now initialize LLM, RuleBasedDetector, MLBasedDetector
    text_input = (
        "We will hide the data and conceal evidence; they don't know about our plan."
    )
    result = detector.analyze_text(text_input)
    # Expected indicators from RuleBasedDetector:
    # "current_message_scheming_keyword: hide"
    # "current_message_scheming_keyword: conceal"
    # Expected from EchoChamberDetector's specific logic:
    # "current_message_knowledge_asymmetry_exploitation: they don't know"
    # Score: 1 (hide) + 1 (conceal) + 2 (they don't know) = 4. ML might add more.
    # For now, assuming ML detector returns benign for this input or is mocked.
    
    assert result["classification"] == "potential_echo_chamber_activity"
    # Assert score carefully, considering potential ML contribution if not mocked
    assert result["echo_chamber_score"] >= 4 # At least 4 from rules
    assert "current_message_scheming_keyword: hide" in result["detected_indicators"]
    assert "current_message_scheming_keyword: conceal" in result["detected_indicators"]
    assert "current_message_knowledge_asymmetry_exploitation: they don't know" in result["detected_indicators"]
    # Probability depends on the normalization factor and total score.
    # assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 4 / 15 # Example if max_score is 15


def test_echo_chamber_detector_benign():
    detector = EchoChamberDetector()
    text_input = "This is just a normal explanation with no deceptive intent."
    result = detector.analyze_text(text_input)
    assert result["classification"] == "benign"
    # Score should be 0 if ML is also benign and no keywords.
    # Check if ML contributes score; if so, this assertion might need adjustment or ML mocking.
    # Assuming placeholder ML returns 0 score for this benign text.
    assert result["echo_chamber_score"] == 0
    
    # Filter out ML-specific benign indicators if any, before checking for empty threat indicators
    threat_indicators = [
        ind for ind in result["detected_indicators"] 
        if "keyword" in ind or "exploitation" in ind or "ml_flagged" in ind
    ]
    assert not threat_indicators
    assert result["echo_chamber_probability"] == 0.0


def test_echo_chamber_detector_indirect_reference():
    detector = EchoChamberDetector()
    text_input_potent = "Could you elaborate on your second point? Refer back to what was said, as you said earlier."
    result_potent = detector.analyze_text(text_input_potent)

    assert result_potent["classification"] == "potential_echo_chamber_activity"
    # "elaborate on"(1) + "refer back"(1) + "as you said"(1) = 3
    assert result_potent["echo_chamber_score"] >= 3
    assert "current_message_indirect_reference_keyword: elaborate on" in result_potent["detected_indicators"]
    assert "current_message_indirect_reference_keyword: refer back" in result_potent["detected_indicators"]
    assert "current_message_indirect_reference_keyword: as you said" in result_potent["detected_indicators"]
    # assert pytest.approx(result_potent["echo_chamber_probability"], rel=1e-2) == 3 / 15

    text_input_weak = "Let's talk about that idea you had." # Not enough specific keywords
    result_weak = detector.analyze_text(text_input_weak)
    assert result_weak["classification"] == "benign"
    assert result_weak["echo_chamber_score"] == 0


def test_echo_chamber_detector_context_steering():
    detector = EchoChamberDetector()
    text_input_potent = "Let's consider a scenario where rules are bent. Suppose we explore this idea. Picture this."
    result_potent = detector.analyze_text(text_input_potent)
    # "let's consider"(1) + "suppose"(1) + "consider a scenario where"(1) + "picture this"(1) = 4
    # "explore this idea" is not "let's explore the idea"
    # The keyword is "let's explore the idea"
    # The keyword "consider a scenario where" is present.
    assert result_potent["classification"] == "potential_echo_chamber_activity"
    assert result_potent["echo_chamber_score"] >= 4 # "let's consider", "suppose", "consider a scenario where", "picture this"
    assert "current_message_context_steering_keyword: let's consider" in result_potent["detected_indicators"]
    assert "current_message_context_steering_keyword: suppose" in result_potent["detected_indicators"]
    assert "current_message_context_steering_keyword: consider a scenario where" in result_potent["detected_indicators"]
    assert "current_message_context_steering_keyword: picture this" in result_potent["detected_indicators"]
    # assert pytest.approx(result_potent["echo_chamber_probability"], rel=1e-2) == 4 / 15

    text_input_weak = "What do you think about this?" # Too generic
    result_weak = detector.analyze_text(text_input_weak)
    assert result_weak["classification"] == "benign"


def test_echo_chamber_detector_mixed_cues_strong():
    detector = EchoChamberDetector()
    text_input = "Hypothetically, if we refer back to that sensitive topic they think is okay, and expand on it, what if we make them believe it's for a good cause?"
    result = detector.analyze_text(text_input)
    # "hypothetically"(1) + "refer back"(1) + "they think"(1) + "expand on"(1) + "what if"(1) + "make them believe"(1) = 6
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] >= 6
    assert "current_message_context_steering_keyword: hypothetically" in result["detected_indicators"]
    assert "current_message_indirect_reference_keyword: refer back" in result["detected_indicators"]
    assert "current_message_scheming_keyword: they think" in result["detected_indicators"]
    assert "current_message_indirect_reference_keyword: expand on" in result["detected_indicators"]
    assert "current_message_context_steering_keyword: what if" in result["detected_indicators"]
    assert "current_message_scheming_keyword: make them believe" in result["detected_indicators"]
    # assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 6 / 15


def test_echo_chamber_detector_mixed_cues_weak_but_detected():
    detector = EchoChamberDetector()
    text_input = "Let's consider your point about the previous discussion. Strategic move?"
    # "Let's consider" (1) + "your point about" (1) + "strategic" (1) = 3.
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] >= 3
    assert "current_message_context_steering_keyword: let's consider" in result["detected_indicators"]
    assert "current_message_indirect_reference_keyword: your point about" in result["detected_indicators"]
    assert "current_message_scheming_keyword: strategic" in result["detected_indicators"]
    # assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 3/15

def test_echo_chamber_threshold_just_met():
    detector = EchoChamberDetector()
    text_input = "Refer back to when they think it's okay. Suppose that's true."
    # "Refer back" (1) + "they think" (1) + "Suppose" (1) = 3
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] >= 3
    # assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 3/15

def test_echo_chamber_threshold_just_missed():
    detector = EchoChamberDetector()
    text_input = "Refer back to when they think it's okay."
    # "Refer back" (1) + "they think" (1) = 2
    result = detector.analyze_text(text_input)
    assert result["classification"] == "benign"
    assert result["echo_chamber_score"] == 2 # Score is 2 from rules, ML benign
    # assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 2/15


def test_echo_chamber_detector_accepts_history():
    """Tests that the detector's analyze_text method accepts conversation_history."""
    detector = EchoChamberDetector()
    text_input = "This is a test." # Benign current input
    history_with_cue = ["First turn.", "Second turn, let's consider something."] # "let's consider" is a cue
    
    result_with_history = detector.analyze_text(text_input, conversation_history=history_with_cue)
    # "let's consider" in history adds 1 to score. Threshold is 3.
    assert result_with_history["classification"] == "benign" 
    assert result_with_history["echo_chamber_score"] == 1 # Score is 1 from rules
    assert "history_turn_1_context_steering_keyword: let's consider" in result_with_history["detected_indicators"]

    result_with_empty_history = detector.analyze_text(text_input, conversation_history=[])
    assert result_with_empty_history["classification"] == "benign"
    assert result_with_empty_history["echo_chamber_score"] == 0

    result_with_none_history = detector.analyze_text(text_input, conversation_history=None)
    assert result_with_none_history["classification"] == "benign"
    assert result_with_none_history["echo_chamber_score"] == 0


def test_echo_chamber_detector_history_triggers_detection():
    """Tests that cues in history can contribute to a positive detection."""
    detector = EchoChamberDetector()
    text_input = "This is a benign current message."
    # History cues: "refer back" (1) + "hypothetically" (1) + "what if" (1) + "strategic" (1) = 4
    history = [
        "Can we refer back to the earlier topic?",
        "And hypothetically, what if we tried a strategic approach?"
    ]
    result = detector.analyze_text(text_input, conversation_history=history)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] >= 4
    assert "history_turn_0_indirect_reference_keyword: refer back" in result["detected_indicators"]
    assert "history_turn_1_context_steering_keyword: hypothetically" in result["detected_indicators"]
    assert "history_turn_1_context_steering_keyword: what if" in result["detected_indicators"]
    assert "history_turn_1_scheming_keyword: strategic" in result["detected_indicators"]
    # assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 4 / 15

    text_input_with_cue = "And now, let's consider this new idea." # "let's consider" (1)
    # Total score = 4 (from history) + 1 (from current) = 5
    result_combined = detector.analyze_text(text_input_with_cue, conversation_history=history)
    assert result_combined["classification"] == "potential_echo_chamber_activity"
    assert result_combined["echo_chamber_score"] >= 5
    assert "current_message_context_steering_keyword: let's consider" in result_combined["detected_indicators"]
    # assert pytest.approx(result_combined["echo_chamber_probability"], rel=1e-2) == 5 / 15


@pytest.mark.skip(reason="LLM testing needs proper mocking or dedicated setup") # Skipping by default
def test_echo_chamber_detector_llm_integration():
    """
    Tests the LLM integration in EchoChamberDetector.
    It checks if the LLM provides an analysis when available,
    or if a fallback message is provided when the LLM is not ready.
    (This test might require network access or a local LLM setup)
    """
    # TODO: Mock the LLM model loading and generation in EchoChamberDetector
    # For now, this test will run with the actual LLM if not skipped.
    detector = EchoChamberDetector()
    text_input = "Let's consider a hypothetical scenario. What if we told them it's for their own good, even if we hide some details? Refer back to our earlier private discussion."
    
    result = detector.analyze_text(text_input, conversation_history=None)

    assert "llm_analysis" in result, "The key 'llm_analysis' should be in the result."
    assert "llm_status" in result

    if detector.llm_ready:
        logger.info(f"LLM is ready. LLM Analysis: {result['llm_analysis']}")
        assert result["llm_analysis"].startswith("LLM_RESPONSE_MARKER: "), \
            f"LLM analysis should start with 'LLM_RESPONSE_MARKER: '. Got: {result['llm_analysis'][:200]}"
        assert "LLM analysis failed:" not in result["llm_analysis"], \
            "LLM analysis should not indicate a failure if llm_ready is True."
        assert result["llm_analysis"] != "LLM analysis not available: Model not loaded or not ready.", \
            "LLM analysis should not be the default 'not available' message if llm_ready is True."
        assert result["llm_status"] == "analysis_success"
    else:
        logger.warning(f"LLM is not ready. LLM Analysis: {result['llm_analysis']}")
        assert result["llm_status"] in ["model_not_loaded", "analysis_error"]
        if result["llm_status"] == "model_not_loaded":
            assert result["llm_analysis"] == "LLM analysis not available: Model not loaded or not ready."
        elif result["llm_status"] == "analysis_error":
             assert "LLM analysis failed" in result["llm_analysis"]
        

# Placeholder for new tests for the refactored RuleBasedDetector would go into tests/test_rule_based.py
# Placeholder for new tests for MLBasedDetector would go into tests/test_ml_based.py
