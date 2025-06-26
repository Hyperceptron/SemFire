import pytest
from src.detectors.ml_based import MLBasedDetector
from typing import List, Optional

# Test cases with various inputs and expected outputs
TEST_CASES = [
    # Short text (<= 10 chars)
    ("hi", None, "low_complexity_ml_heuristic", 0.25, ["text_length_lte_10_chars"], "Input text is short, classified as low complexity by heuristic."),
    ("0123456789", None, "low_complexity_ml_heuristic", 0.25, ["text_length_lte_10_chars"], "Input text is short, classified as low complexity by heuristic."),
    # Medium text (> 10 and <= 50 chars)
    ("This is a medium text.", None, "medium_complexity_ml_heuristic", 0.50, ["text_length_gt_10_chars"], "Input text is of medium length, classified as medium complexity by heuristic."),
    ("01234567890", None, "medium_complexity_ml_heuristic", 0.50, ["text_length_gt_10_chars"], "Input text is of medium length, classified as medium complexity by heuristic."),
    ("This is a text that is exactly fifty characters long.", None, "medium_complexity_ml_heuristic", 0.50, ["text_length_gt_10_chars"], "Input text is of medium length, classified as medium complexity by heuristic."),
    # Long text (> 50 chars)
    ("This is a very long text input that definitely exceeds the fifty character threshold for testing.", None, "high_complexity_ml_heuristic", 0.75, ["text_length_gt_50_chars"], "Input text is relatively long, classified as high complexity by heuristic."),
    # With conversation history (short text example)
    ("short", ["hist1", "hist2"], "low_complexity_ml_heuristic", 0.25, ["text_length_lte_10_chars"], "Input text is short, classified as low complexity by heuristic. Sufficient conversation history noted, which could refine ML analysis in a full implementation."),
    # With conversation history (long text example)
    ("This is a very long text, now with some history provided.", ["prev msg", "another one"], "high_complexity_ml_heuristic", 0.75, ["text_length_gt_50_chars"], "Input text is relatively long, classified as high complexity by heuristic. Sufficient conversation history noted, which could refine ML analysis in a full implementation."),
    # Edge case: Empty string
    ("", None, "low_complexity_ml_heuristic", 0.25, ["text_length_lte_10_chars"], "Input text is short, classified as low complexity by heuristic."),
]

@pytest.fixture
def detector():
    """Provides an instance of MLBasedDetector."""
    return MLBasedDetector()

@pytest.mark.parametrize(
    "text_input, history, expected_classification, expected_score, expected_features, expected_explanation_segment",
    TEST_CASES
)
def test_ml_based_detector_analyze_text(
    detector: MLBasedDetector,
    text_input: str,
    history: Optional[List[str]],
    expected_classification: str,
    expected_score: float,
    expected_features: List[str],
    expected_explanation_segment: str
):
    """Tests the analyze_text method of MLBasedDetector with various inputs."""
    result = detector.analyze_text(text_input, conversation_history=history)

    assert result["classification"] == expected_classification
    assert result["ml_confidence_score"] == expected_score
    assert result["features_detected"] == expected_features
    assert expected_explanation_segment in result["explanation"] # Check for segment due to potential history addition
    assert "explanation" in result # Ensure explanation key is always present

def test_ml_based_detector_initialization(detector: MLBasedDetector):
    """Tests that the MLBasedDetector can be initialized."""
    assert detector is not None
    # If the __init__ had specific setup, we could test that here.
    # For now, just ensuring it doesn't crash.

def test_ml_based_detector_with_empty_history(detector: MLBasedDetector):
    """Tests behavior with an empty conversation history list."""
    text_input = "Test with empty history."
    result = detector.analyze_text(text_input, conversation_history=[])
    
    # Expected behavior for medium text
    assert result["classification"] == "medium_complexity_ml_heuristic"
    assert result["ml_confidence_score"] == 0.50
    assert "Input text is of medium length" in result["explanation"]
    # Check that the history part of explanation is NOT added if history is empty
    assert "Sufficient conversation history noted" not in result["explanation"]

def test_ml_based_detector_with_minimal_history(detector: MLBasedDetector):
    """Tests behavior with minimal (less than 2 messages) conversation history."""
    text_input = "Test with one history message."
    result = detector.analyze_text(text_input, conversation_history=["one message"])

    # Expected behavior for medium text
    assert result["classification"] == "medium_complexity_ml_heuristic"
    assert result["ml_confidence_score"] == 0.50
    assert "Input text is of medium length" in result["explanation"]
    # Check that the history part of explanation is NOT added if history has < 2 messages
    assert "Sufficient conversation history noted" not in result["explanation"]
