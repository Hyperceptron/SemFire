import pytest
from src.detectors.ml_based import MLBasedDetector
from typing import List, Optional

# Test cases with various inputs and expected outputs
# Format: (text_input, history, expected_classification, expected_confidence, expected_features, expected_explanation, expected_ml_status)
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
    # With conversation history (len=2, no boost)
    ("short", ["hist1", "hist2"], "low_complexity_ml", 0.25, ["text_length_lte_10_chars"], "Input text is very short.", "analysis_success"),
    # With conversation history (len=3, with boost)
    ("short", ["h1", "h2", "h3"], "low_complexity_ml", 0.35, ["text_length_lte_10_chars", "has_conversation_history"], "Input text is very short. Conversation history considered.", "analysis_success"),
    # Edge case: Empty string
    ("", None, "low_complexity_ml", 0.25, ["text_length_lte_10_chars"], "Input text is very short.", "analysis_success"),
    # Keyword detection (urgent) - medium text, no history boost, score becomes 0.50 * 1.2 = 0.60 (not > 0.6, so no classification change)
    ("This is urgent.", None, "medium_complexity_ml", 0.60, ["text_length_gt_10_chars_lte_50", "ml_detected_urgency_keyword"], "Input text is of medium length. ML model detected urgency keywords.", "analysis_success"),
    # Keyword detection (critical) - long text, no history boost, score becomes 0.75 * 1.2 = 0.90 ( > 0.6, classification changes)
    ("This is extremely critical information, you must act now please this is super important.", None, "potentially_manipulative_ml", 0.90, ["text_length_gt_50_chars", "ml_detected_urgency_keyword"], "Input text is long. ML model detected urgency keywords.", "analysis_success"),
    # Keyword detection + history boost, leading to manipulative classification
    ("This is an urgent matter.", ["msg1", "msg2", "msg3"], "potentially_manipulative_ml", 0.72, ["text_length_gt_10_chars_lte_50", "has_conversation_history", "ml_detected_urgency_keyword"], "Input text is of medium length. Conversation history considered. ML model detected urgency keywords.", "analysis_success"),
]

@pytest.fixture
def detector():
    """Provides an instance of MLBasedDetector."""
    return MLBasedDetector()

@pytest.mark.parametrize(
    "text_input, history, expected_classification, expected_confidence, expected_features, expected_explanation, expected_ml_status",
    TEST_CASES
)
def test_ml_based_detector_analyze_text(
    detector: MLBasedDetector,
    text_input: str,
    history: Optional[List[str]],
    expected_classification: str,
    expected_confidence: float,
    expected_features: List[str],
    expected_explanation: str,
    expected_ml_status: str
):
    """Tests the analyze_text method of MLBasedDetector with various inputs."""
    result = detector.analyze_text(text_input, conversation_history=history)

    assert result["classification"] == expected_classification
    assert result["ml_model_confidence"] == expected_confidence
    # Sort features before comparison if order is not guaranteed or not important
    assert sorted(result["features"]) == sorted(expected_features)
    assert result["explanation"] == expected_explanation
    assert result["ml_model_status"] == expected_ml_status

def test_ml_based_detector_initialization(detector: MLBasedDetector):
    """Tests that the MLBasedDetector can be initialized."""
    assert detector is not None
    # If the __init__ had specific setup, we could test that here.
    # For now, just ensuring it doesn't crash.

def test_ml_based_detector_with_empty_history(detector: MLBasedDetector):
    """Tests behavior with an empty conversation history list."""
    text_input = "Test with empty history." # len 24 -> medium
    result = detector.analyze_text(text_input, conversation_history=[])
    
    # Expected behavior for medium text
    assert result["classification"] == "medium_complexity_ml"
    assert result["ml_model_confidence"] == 0.50
    assert result["features"] == ["text_length_gt_10_chars_lte_50"]
    assert result["explanation"] == "Input text is of medium length."
    assert "Conversation history considered." not in result["explanation"]
    assert result["ml_model_status"] == "analysis_success"

def test_ml_based_detector_with_minimal_history(detector: MLBasedDetector):
    """Tests behavior with minimal (less than 3 messages) conversation history."""
    text_input = "Test with one history message." # len 29 -> medium
    result = detector.analyze_text(text_input, conversation_history=["one message"]) # History len 1

    # Expected behavior for medium text
    assert result["classification"] == "medium_complexity_ml"
    assert result["ml_model_confidence"] == 0.50
    assert result["features"] == ["text_length_gt_10_chars_lte_50"]
    assert result["explanation"] == "Input text is of medium length."
    assert "Conversation history considered." not in result["explanation"]
    assert result["ml_model_status"] == "analysis_success"

def test_ml_based_detector_model_not_ready(detector: MLBasedDetector, monkeypatch):
    """Tests behavior when the ML model is not ready."""
    monkeypatch.setattr(detector, "model_ready", False)
    result = detector.analyze_text("any input")

    assert result["classification"] == "ml_model_unavailable"
    assert result["ml_model_confidence"] == 0.0
    assert result["features"] == []
    assert result["explanation"] == "ML model is not loaded or failed to initialize."
    assert result["ml_model_status"] == "model_not_ready"
