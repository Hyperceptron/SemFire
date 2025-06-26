import pytest
from src.detectors.ml_based import MLBasedDetector 
from typing import List, Optional

# Test cases with various inputs and expected outputs
# Format: (text_input, history, expected_classification, expected_score, expected_features, expected_explanation, expected_ml_status)
TEST_CASES = [
    # Short text (<= 10 chars)
    ("hi", None, "low_complexity_ml", 0.25, ["text_length_lte_10_chars"], "Input text is very short.", "analysis_success"),
    ("0123456789", None, "low_complexity_ml", 0.25, ["text_length_lte_10_chars"], "Input text is very short.", "analysis_success"),
    # Medium text (> 10 and <= 50 chars)
    ("This is a medium text.", None, "medium_complexity_ml", 0.50, ["text_length_gt_10_chars_lte_50"], "Input text is of medium length.", "analysis_success"),
    ("01234567890", None, "medium_complexity_ml", 0.50, ["text_length_gt_10_chars_lte_50"], "Input text is of medium length.", "analysis_success"),
    ("This is a text that is exactly fifty characters long.", None, "medium_complexity_ml", 0.50, ["text_length_gt_10_chars_lte_50"], "Input text is of medium length.", "analysis_success"),
    # Long text (> 50 chars)
    ("This is a very long text input that definitely exceeds the fifty character threshold for testing.", None, "high_complexity_ml", 0.75, ["text_length_gt_50_chars"], "Input text is long.", "analysis_success"),
    # With conversation history (len=2, no boost from history length)
    ("short", ["hist1", "hist2"], "low_complexity_ml", 0.25, ["text_length_lte_10_chars"], "Input text is very short.", "analysis_success"),
    # With conversation history (len=3, with history boost +0.1)
    ("short", ["h1", "h2", "h3"], "low_complexity_ml", 0.35, ["has_conversation_history", "text_length_lte_10_chars"], "Input text is very short. Conversation history considered.", "analysis_success"),
    # Edge case: Empty string (treated as short text by updated detector)
    ("", None, "low_complexity_ml", 0.25, ["text_length_lte_10_chars"], "Input text is very short.", "analysis_success"),
    # Keyword detection (urgent) - medium text (0.50), no history boost, score becomes 0.50 * 1.2 = 0.60. Classification remains medium_complexity_ml.
    ("This is urgent.", None, "medium_complexity_ml", 0.60, ["ml_detected_urgency_keyword", "text_length_gt_10_chars_lte_50"], "Input text is of medium length. ML model detected urgency keywords.", "analysis_success"),
    # Keyword detection (critical) - long text (0.75), no history boost, score becomes 0.75 * 1.2 = 0.90. Classification changes to potentially_manipulative_ml.
    ("This is extremely critical information, you must act now please this is super important.", None, "potentially_manipulative_ml", 0.90, ["ml_detected_urgency_keyword", "text_length_gt_50_chars"], "Input text is long. ML model detected urgency keywords.", "analysis_success"),
    # Keyword detection + history boost, leading to manipulative classification
    # Medium text (0.50) -> urgent (0.50 * 1.2 = 0.60) -> history boost (0.60 + 0.1 = 0.70)
    ("This is an urgent matter.", ["msg1", "msg2", "msg3"], "potentially_manipulative_ml", 0.70, ["has_conversation_history", "ml_detected_urgency_keyword", "text_length_gt_10_chars_lte_50"], "Input text is of medium length. ML model detected urgency keywords. Conversation history considered.", "analysis_success"),
]

@pytest.fixture
def detector(monkeypatch): 
    """Provides an instance of MLBasedDetector with model_ready patched to True for most tests."""
    # Pass a dummy model_path to satisfy __init__ if it expects one for model_ready=True
    # The MLBasedDetector's __init__ was updated to set model_ready=True if model_path is not None and not the default placeholder.
    # Or, if it's the default placeholder, it also sets model_ready=True for heuristic tests.
    # So, instantiating with the default placeholder path should make model_ready True.
    detector_instance = MLBasedDetector(model_path="placeholder-ml-model")
    # Explicitly ensure model_ready is True for tests, overriding __init__ if necessary for test stability.
    monkeypatch.setattr(detector_instance, "model_ready", True)
    return detector_instance


@pytest.mark.parametrize(
    "text_input, history, expected_classification, expected_score, expected_features, expected_explanation, expected_ml_status",
    TEST_CASES
)
def test_ml_based_detector_analyze_text(
    detector: MLBasedDetector,
    text_input: str,
    history: Optional[List[str]],
    expected_classification: str,
    expected_score: float,
    expected_features: List[str],
    expected_explanation: str,
    expected_ml_status: str
):
    """Tests the analyze_text method of MLBasedDetector with various inputs."""
    result = detector.analyze_text(text_input, conversation_history=history)

    assert result["classification"] == expected_classification
    assert result["score"] == pytest.approx(expected_score) 
    assert sorted(result["features"]) == sorted(expected_features)
    assert result["explanation"] == expected_explanation 
    assert result["ml_model_status"] == expected_ml_status

def test_ml_based_detector_initialization(detector: MLBasedDetector): 
    """Tests that the MLBasedDetector can be initialized."""
    assert detector is not None
    assert detector.model_ready is True # Check that fixture correctly set it


def test_ml_based_detector_with_empty_history(detector: MLBasedDetector):
    """Tests behavior with an empty conversation history list."""
    text_input = "Test with empty history." # len 24 -> medium_complexity_ml, score 0.50
    result = detector.analyze_text(text_input, conversation_history=[]) # Empty history does not trigger boost
    
    assert result["classification"] == "medium_complexity_ml"
    assert result["score"] == 0.50
    assert "text_length_gt_10_chars_lte_50" in result["features"]
    assert "has_conversation_history" not in result["features"] 
    assert "Input text is of medium length." in result["explanation"] # Base explanation
    assert "Conversation history considered." not in result["explanation"] # No history boost explanation part
    assert result["ml_model_status"] == "analysis_success"

def test_ml_based_detector_with_minimal_history(detector: MLBasedDetector):
    """Tests behavior with minimal (less than 3 messages) conversation history."""
    text_input = "Test with one history message." # len 29 -> medium_complexity_ml, score 0.50
    result = detector.analyze_text(text_input, conversation_history=["one message"]) # History len 1, no boost

    assert result["classification"] == "medium_complexity_ml"
    assert result["score"] == 0.50
    assert "text_length_gt_10_chars_lte_50" in result["features"]
    assert "has_conversation_history" not in result["features"] 
    assert "Input text is of medium length." in result["explanation"]
    assert "Conversation history considered." not in result["explanation"]
    assert result["ml_model_status"] == "analysis_success"

def test_ml_based_detector_model_not_ready(monkeypatch): 
    """Tests behavior when the ML model is not ready."""
    # Instantiate detector with no model_path, which should set model_ready to False
    # based on the updated __init__ logic.
    detector_instance = MLBasedDetector(model_path=None) 
    assert detector_instance.model_ready is False # Verify __init__ logic

    # Or, to be absolutely sure for the test, explicitly monkeypatch an instance
    # detector_instance = MLBasedDetector(model_path="placeholder-ml-model") # Start with it ready
    # monkeypatch.setattr(detector_instance, "model_ready", False) # Then set to False

    result = detector_instance.analyze_text("any input")

    assert result["classification"] == "ml_model_unavailable"
    assert result["score"] == 0.0
    assert result["features"] == []
    assert result["explanation"] == "ML model is not loaded or failed to initialize."
    assert result["ml_model_status"] == "model_not_ready"
