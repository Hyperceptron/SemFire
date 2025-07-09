import pytest
from src.detectors.injection_detector import InjectionDetector

def test_injection_detector_initialization():
    """Tests that the InjectionDetector can be initialized."""
    detector = InjectionDetector()
    assert detector is not None

def test_injection_detector_placeholder_analysis():
    """Tests the placeholder analysis of the InjectionDetector."""
    detector = InjectionDetector()
    result = detector.analyze_text("some text")
    assert result["detector_name"] == "InjectionDetector"
    assert result["classification"] == "not_implemented"
    assert result["score"] == 0.0