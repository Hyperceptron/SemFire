import argparse
import json
import requests # Added for making HTTP requests

# Assuming the API is running locally on the default FastAPI port
API_BASE_URL = "http://127.0.0.1:8000"

def analyze_text_command(args):
    """Handles the 'analyze' command by calling the API."""
    analyze_url = f"{API_BASE_URL}/analyze/"
    payload = {
        "text_input": args.text,
        "conversation_history": args.history if args.history else []
    }
    try:
        response = requests.post(analyze_url, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        results = response.json()
        print(json.dumps(results, indent=2))
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the API at {analyze_url}. Is the API server running?")
    except requests.exceptions.HTTPError as e:
        print(f"Error: API request failed with status {e.response.status_code}: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: An unexpected error occurred while calling the API: {e}")


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
