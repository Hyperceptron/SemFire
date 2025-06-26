import argparse
import json
# Removed: import requests
from src.detectors.rule_based import EchoChamberDetector # Added for local inference
from src.detectors.ml_based import MLBasedDetector # Added for ML-based detector

# Removed: API_BASE_URL

def analyze_text_command(args):
    """Handles the 'analyze' command by performing local inference with the selected detector."""
    if args.detector_type == "rule":
        detector = EchoChamberDetector()
        print("Using Rule-Based Detector (EchoChamberDetector)...")
    elif args.detector_type == "ml":
        # You might want to pass a model path to MLBasedDetector if needed, e.g., from another CLI arg
        detector = MLBasedDetector()
        print("Using ML-Based Detector (MLBasedDetector)...")
    else:
        # This case should not be reached if choices are enforced by argparse
        print(f"Error: Unknown detector type '{args.detector_type}'. Defaulting to rule-based.")
        detector = EchoChamberDetector()

    results = detector.analyze_text(args.text, args.history if args.history else [])
    print(json.dumps(results, indent=2))

def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(description="AI Deception Detection Toolkit CLI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True # Ensure a command is always given

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text for deception cues.")
    analyze_parser.add_argument("text", help="The text input to analyze (e.g., current message).")
    analyze_parser.add_argument("--history", nargs="*", help="Optional conversation history, ordered from oldest to newest.")
    analyze_parser.add_argument(
        "--detector_type",
        type=str,
        choices=["rule", "ml"],
        default="rule",
        help="Type of detector to use: 'rule' for EchoChamberDetector, 'ml' for MLBasedDetector (default: rule)."
    )
    analyze_parser.set_defaults(func=analyze_text_command)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        # This case should ideally not be reached if subparsers.required = True
        # and all subparsers have a default function.
        # However, it's good practice for fallback or if a command is misconfigured.
        parser.print_help()


if __name__ == "__main__":
    main()
