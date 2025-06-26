import argparse
import json
from src.semantic_firewall import SemanticFirewall # Import SemanticFirewall

# Removed: EchoChamberDetector and MLBasedDetector direct imports as SemanticFirewall handles them.
# Removed: API_BASE_URL

def analyze_text_command(args):
    """Handles the 'analyze' command using SemanticFirewall for combined analysis."""
    firewall = SemanticFirewall()
    print("Using SemanticFirewall for combined analysis...")
    
    # Call analyze_conversation on the firewall instance
    # SemanticFirewall's analyze_conversation method will use all its configured detectors
    results = firewall.analyze_conversation(
        current_message=args.text,
        conversation_history=args.history if args.history else []
    )
    print(json.dumps(results, indent=2))

    # Optionally, you could also call and print the result of is_manipulative
    is_manipulative_flag = firewall.is_manipulative(
        current_message=args.text,
        conversation_history=args.history if args.history else []
        # threshold=args.threshold # If you add a threshold argument to CLI
    )
    print(f"\nOverall manipulative assessment (default threshold): {is_manipulative_flag}")


def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(description="AI Deception Detection Toolkit CLI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True # Ensure a command is always given

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

    if hasattr(args, 'func'):
        args.func(args)
    else:
        # This case should ideally not be reached if subparsers.required = True
        # and all subparsers have a default function.
        # However, it's good practice for fallback or if a command is misconfigured.
        parser.print_help()


if __name__ == "__main__":
    main()
