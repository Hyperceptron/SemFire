# Core detectors
from .rule_based import RuleBasedDetector
from .ml_based import MLBasedDetector # Newly created ML detector

# Orchestrating detector that uses RuleBasedDetector and MLBasedDetector, and includes LLM.
# This 'echo_chamber.py' is now the primary, refactored EchoChamberDetector.
from .echo_chamber import EchoChamberDetector 

# Note:
# - src/detectors/generic_rule_based_detector.py is to be deleted.
# - src/detectors/echo_chamber_detector.py (the old complex one, whose LLM logic is now in the new EchoChamberDetector) is to be deleted.

__all__ = [
    "RuleBasedDetector",      # For direct rule-based analysis (can be configured with different rule sets)
    "MLBasedDetector",        # For direct ML-based analysis
    "EchoChamberDetector",    # For comprehensive echo chamber analysis, leveraging the above two
                              # and its own LLM analysis.
]
