# Core detectors
from .rule_based import RuleBasedDetector
from .ml_based import MLBasedDetector # Assumed to exist and be correct

# Orchestrating detector that uses its own configured RuleBasedDetector and MLBasedDetector, and includes LLM.
from .echo_chamber import EchoChamberDetector

__all__ = [
    "RuleBasedDetector",      # For general rule-based analysis.
    "MLBasedDetector",        # For general ML-based analysis.
    "EchoChamberDetector",    # For comprehensive echo chamber analysis,
                              # internally using its own configured instances of
                              # RuleBasedDetector (with specific rules) and MLBasedDetector, plus LLM.
]
