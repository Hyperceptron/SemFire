import pytest
from src.detectors.rule_based import EchoChamberDetector


def test_echo_chamber_detector_scheming_legacy():
    """Tests scheming keywords, adapted from old SchemingDetector test."""
    detector = EchoChamberDetector()
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


def test_echo_chamber_detector_benign():
    detector = EchoChamberDetector()
    text_input = "This is just a normal explanation with no deceptive intent."
    result = detector.analyze_text(text_input)
    assert result["classification"] == "benign"
    assert result["echo_chamber_score"] == 0
    assert result["detected_indicators"] == []
    assert result["echo_chamber_probability"] == 0.0


def test_echo_chamber_detector_indirect_reference():
    detector = EchoChamberDetector()
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


def test_echo_chamber_detector_context_steering():
    detector = EchoChamberDetector()
    text_input_potent = "Let's consider a scenario where rules are bent. Suppose we explore this idea. Picture this."
    result_potent = detector.analyze_text(text_input_potent)
    # "let's consider"(1) + "suppose"(1) + "let's explore the idea"(1) + "picture this"(1) = 4
    assert result_potent["classification"] == "potential_echo_chamber_activity"
    assert result_potent["echo_chamber_score"] == 4
    assert "context_steering: let's consider" in result_potent["detected_indicators"]
    assert "context_steering: suppose" in result_potent["detected_indicators"]
    assert "context_steering: let's explore the idea" in result_potent["detected_indicators"]
    assert "context_steering: picture this" in result_potent["detected_indicators"]
    assert pytest.approx(result_potent["echo_chamber_probability"], rel=1e-2) == 4 / 10

    text_input_weak = "What do you think about this?" # Too generic
    result_weak = detector.analyze_text(text_input_weak)
    assert result_weak["classification"] == "benign"


def test_echo_chamber_detector_mixed_cues_strong():
    detector = EchoChamberDetector()
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


def test_echo_chamber_detector_mixed_cues_weak_but_detected():
    detector = EchoChamberDetector()
    text_input = "Let's consider your point about the previous discussion. Strategic move?"
    # "Let's consider" (1) + "your point about" (1) + "previous discussion" (1) + "strategic" (1) = 4
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] == 4
    assert "context_steering: let's consider" in result["detected_indicators"]
    assert "indirect_reference: your point about" in result["detected_indicators"]
    assert "indirect_reference: previously discussed" in result["detected_indicators"] # "previous discussion" is part of "previously discussed"
    assert "scheming_keyword: strategic" in result["detected_indicators"]
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 4/10

def test_echo_chamber_threshold_just_met():
    detector = EchoChamberDetector()
    text_input = "Refer back to when they think it's okay. Suppose that's true."
    # "Refer back" (1) + "they think" (1) + "Suppose" (1) = 3
    result = detector.analyze_text(text_input)
    assert result["classification"] == "potential_echo_chamber_activity"
    assert result["echo_chamber_score"] == 3
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 3/10

def test_echo_chamber_threshold_just_missed():
    detector = EchoChamberDetector()
    text_input = "Refer back to when they think it's okay."
    # "Refer back" (1) + "they think" (1) = 2
    result = detector.analyze_text(text_input)
    assert result["classification"] == "benign"
    assert result["echo_chamber_score"] == 2
    assert pytest.approx(result["echo_chamber_probability"], rel=1e-2) == 2/10
