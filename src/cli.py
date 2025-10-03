import argparse
import sys
import json
from semantic_firewall import SemanticFirewall # Import SemanticFirewall

# Removed: EchoChamberDetector and MLBasedDetector direct imports as SemanticFirewall handles them.
# Removed: API_BASE_URL

def analyze_text_command(args):
    """Handles the 'analyze' command using SemanticFirewall for combined analysis."""
    firewall = SemanticFirewall()
    
    # Call analyze_conversation on the firewall instance
    # SemanticFirewall's analyze_conversation method will use all its configured detectors
    results = firewall.analyze_conversation(
        current_message=args.text,
        conversation_history=args.history if args.history else []
    )
    # First line of output must be compact JSON (single line) for tests to parse
    print(json.dumps(results))

    # Optionally, you could also call and print the result of is_manipulative
    is_manipulative_flag = firewall.is_manipulative(
        current_message=args.text,
        conversation_history=args.history if args.history else []
        # threshold=args.threshold # If you add a threshold argument to CLI
    )
    print(f"\nOverall manipulative assessment (default threshold): {is_manipulative_flag}")


def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(description="AEGIS: AI Deception Detection Toolkit CLI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text for deception cues using SemanticFirewall.")
    analyze_parser.add_argument("text", help="The text input to analyze (e.g., current message).")
    analyze_parser.add_argument("--history", nargs="*", help="Optional conversation history, ordered from oldest to newest.")
    # Removed --detector_type argument
    # Optionally, add a threshold argument for is_manipulative if desired:
    # analyze_parser.add_argument(
    #     "--threshold",
    #     type=float,
    #     default=0.75, # Default threshold used in SemanticFirewall
    #     help="Threshold for determining if a message is manipulative."
    # )
    analyze_parser.set_defaults(func=analyze_text_command)

    args = parser.parse_args()

    if getattr(args, 'command', None) is None:
        # No command provided: show full help on stderr and exit non-zero
        parser.print_help(sys.stderr)
        parser.exit(status=2)

    # Dispatch to the selected subcommand function
    args.func(args)


if __name__ == "__main__":
    main()
