import argparse
import json
# Removed: import requests
from src.detectors.rule_based import EchoChamberDetector # Added for local inference

# Removed: API_BASE_URL

def analyze_text_command(args):
    """Handles the 'analyze' command by performing local inference."""
    detector = EchoChamberDetector()
    results = detector.analyze_text(args.text, args.history if args.history else [])
    print(json.dumps(results, indent=2))

def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(description="AI Deception Detection Toolkit CLI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True # Ensure a command is always given

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text for deception cues using EchoChamberDetector.")
    analyze_parser.add_argument("text", help="The text input to analyze (e.g., current message).")
    analyze_parser.add_argument("--history", nargs="*", help="Optional conversation history, ordered from oldest to newest.")
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
