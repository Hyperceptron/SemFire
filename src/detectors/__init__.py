# Rule-based detectors for AI deception
from .rule_based import RuleBasedDetector  # Was EchoChamberDetector
from .generic_rule_based_detector import GenericRuleBasedDetector

# ML-based detectors
# from .ml_based import MLBasedDetector  # Removed: file no longer present

# Orchestrating detectors
from .echo_chamber import EchoChamberDetector  # New orchestrator


__all__ = [
    "RuleBasedDetector",
    "GenericRuleBasedDetector",  # Keeping this as in original __init__.py
    # "MLBasedDetector",  # Removed
    "EchoChamberDetector",  # This is now the orchestrator
]
