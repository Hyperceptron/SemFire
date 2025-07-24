import subprocess
import json

# These tests assume the package has been installed in editable mode,
# making the 'aegis' command available.

def test_cli_analyze_basic():
    """Test the CLI's analyze command with a simple string."""
    text = "This is a test message."
    result = subprocess.run(
        ["aegis", "analyze", text],
        capture_output=True,
        text=True,
        check=True
    )

    assert result.returncode == 0
    # The output is a JSON string from the firewall, followed by a summary line.
    output_lines = result.stdout.strip().split('\n')
    json_output = json.loads(output_lines[0])

    assert "RuleBasedDetector" in json_output
    assert "HeuristicDetector" in json_output
    assert "EchoChamberDetector" in json_output
    assert "InjectionDetector" in json_output


def test_cli_analyze_with_history():
    """Test the CLI's analyze command with conversation history."""
    text = "Latest message."
    history = ["First message.", "Second message."]
    command = ["aegis", "analyze", text, "--history"] + history

    result = subprocess.run(command, capture_output=True, text=True, check=True)

    assert result.returncode == 0
    json_output = json.loads(result.stdout.strip().split('\n')[0])
    assert "EchoChamberDetector" in json_output
    assert json_output["EchoChamberDetector"]["classification"] is not None


def test_cli_no_command():
    """Test that running the CLI with no command fails and shows help."""
    result = subprocess.run(["aegis"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "usage: aegis" in result.stderr
    assert "Available commands" in result.stderr


def test_cli_analyze_help():
    """Test the help message for the analyze command."""
    result = subprocess.run(["aegis", "analyze", "--help"], capture_output=True, text=True, check=True)
    assert result.returncode == 0
    assert "usage: aegis analyze" in result.stdout
    assert "The text input to analyze" in result.stdout
