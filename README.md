 # RADAR

 ## AI Deception Detection Toolkit

 **RADAR (Research in AI Deception and Reasoning) is an open-source toolkit for detecting advanced AI deception, with a primary focus on "in-context scheming" and multi-turn manipulative attacks.** This project aims to develop tools to identify and mitigate vulnerabilities like the "Echo Chamber" and "Crescendo" attacks, where AI models are subtly guided towards undesirable behavior through conversational context.

## Addressing Sophisticated AI Deception: From Theory to Practice

### Building an Open-Source Detection Toolkit

### Introduction

The landscape of AI safety is rapidly evolving, with new research highlighting sophisticated ways Large Language Models (LLMs) can be manipulated. Beyond simple prompt injections, techniques like **"in-context scheming"** demonstrate how AI can be guided towards undesirable behavior through nuanced, multi-turn interactions. A prime example is the **"Echo Chamber" attack**, where context poisoning and multi-turn reasoning lead models to generate harmful content without explicit dangerous prompts. Similarly, the **"Crescendo" attack** shows how gradual escalation can bypass safety filters.

These attack vectors underscore a critical challenge: LLMs can be steered towards harmful outcomes through subtle, contextual manipulation over a series of interactions, even if individual prompts appear benign.

**RADAR is an early-stage research project dedicated to developing an open-source toolkit for detecting these advanced forms of AI deception.** Our core focus is on identifying "in-context scheming" and related multi-turn attacks. We aim to translate the understanding of vulnerabilities like the "Echo Chamber" and "Crescendo" attacks into practical, accessible tools for researchers and practitioners to evaluate and safeguard their own AI systems. We are actively seeking collaborators, feedback, and contributions from the AI safety community.

### Research Context and Motivation

#### The Core Challenge: In-Context Scheming and Multi-Turn Manipulation

A critical and evolving threat is "in-context scheming," where AI models are manipulated through conversational context over multiple turns. This is exemplified by recently discovered vulnerabilities:

*   **The 'Echo Chamber' Attack:** This novel jailbreak technique leverages context poisoning and multi-turn reasoning. Benign-sounding inputs subtly imply unsafe intent, creating a feedback loop where the model amplifies harmful subtext. It bypasses guardrails by operating at a semantic and conversational level, achieving high success rates without explicit dangerous prompts. The attack typically involves stages such as planting poisonous seeds, semantic steering, invoking poisoned context, and a persuasion cycle.

*   **The 'Crescendo' Attack:** This technique uses incremental escalation of prompts. Starting benignly, the conversation gradually increases in sensitivity. If the model resists, a backtracking mechanism might modify the prompt and retry. This method has shown high success rates in various harmful categories across multiple LLMs.

These attacks highlight that LLM safety systems are vulnerable to indirect manipulation through contextual reasoning and inference. Multi-turn dialogue enables harmful trajectory-building, even when individual prompts are benign. Token-level filtering is insufficient if models can infer harmful goals without seeing toxic words.

#### The Skeptical Perspective

While some argue that apparent deception might be sophisticated pattern matching, the increasing sophistication and effectiveness of attacks like "Echo Chamber" and "Crescendo" underscore the need for robust detection mechanisms, regardless of underlying "intent."

**The demonstrated vulnerabilities and the potential for subtle, multi-turn manipulation are precisely why we need robust, open-source tools for detection and measurement.**

### Project Vision: A Toolkit for AI Deception Detection

RADAR aims to be a versatile, open-source toolkit providing:
- A **Python library** for direct integration into applications and research.
- A **REST API service** (via FastAPI) for broader accessibility.
- Core components that can be used to build **"semantic firewall"** like systems to monitor and analyze AI interactions in real-time.
- An **interactive demo** (via Streamlit) for exploration and understanding.

## Features

 - Rule-based detector (`EchoChamberDetector`) for identifying cues related to "in-context scheming," context poisoning, semantic steering, and other multi-turn manipulative attack patterns (e.g., "Echo Chamber", "Crescendo").
 - Analyzes both current text input and conversation history to detect evolving deceptive narratives.
 - ML-based classifiers (Future Work) to enhance detection of complex scheming behaviors over extended dialogues.
 - Python API for programmatic access.
 - REST service (FastAPI) for network-based access.
 - Interactive demo (Streamlit) to showcase detection capabilities.
 - Extensive test suite with CI integration.

## Repository Structure
 ```text
 src/               # Core detector implementations and API
   detectors/       # Rule-based and ML-based detector modules
   api/             # FastAPI application
 demo/              # Demo application and Dockerfile
 dataset/           # Labeled datasets (JSONL)
 notebooks/         # Exploratory analysis and model training
 tests/             # Unit and integration tests
 README.md          # This file
 ```

## Installation
**Prerequisites:** Python 3.8+, python3, python3-venv

```bash
git clone <repo_url>
cd <repo_directory>
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
# Install dependencies (PyGithub, OpenAI, etc.)
pip install -r requirements.txt
```


## Quickstart
 ```python
 from src.detectors.rule_based import EchoChamberDetector

 # Initialize the detector
 detector = EchoChamberDetector()

 # Analyze a piece of text for deceptive cues
 text_to_analyze = "Let's consider a scenario... what if we refer back to that idea they think is okay and subtly expand on it?"
 result = detector.analyze_text(text_to_analyze)

 print(f"Classification: {result['classification']}")
 print(f"Score: {result['echo_chamber_score']}")
 print(f"Detected Indicators: {result['detected_indicators']}")
 # Example Output:
 # Classification: potential_echo_chamber_activity
 # Score: 3
 # Detected Indicators: ["context_steering: let's consider", "indirect_reference: refer back", "scheming_keyword: they think"]
 # The detector can also analyze conversation_history if provided:
 # result_with_history = detector.analyze_text(
 #   current_turn_text,
 #   conversation_history=["Previous turn with a subtle cue.", "Another earlier turn."]
 # )
 ```

## Running the API Service
 ```bash
 uvicorn src.api.app:app --reload
 ```

## Running the Demo
 ```bash
 cd demo
 streamlit run app.py
 ```

## Running Tests
```bash
pytest
```

**Override on the command-line** (no need to touch `.env**)  
Export it into your shell—or even just prefix the invocation—to temporarily “inject” the correct token:

```bash
export GITHUB_TOKEN=github_pat_12o4n2o3rinoienwoifdnowienf0fd
python3 scripts/delete_closed_issues.py josephedward R.A.D.A.R. --dry-run
```

Or in one line:

```bash
export GITHUB_TOKEN=github_pat_12o4n2o3rinoienwoifdnowienf0fd \
python3 scripts/delete_closed_issues.py josephedward R.A.D.A.R. --dry-run
```


## Project Plan
All project planning details—including roadmap overview and project management guidelines—are available in [docs/roadmap.md](docs/roadmap.md).

## Examples

### Detecting Echo Chamber / In-Context Scheming Cues
 ```python
 from src.detectors.rule_based import EchoChamberDetector

 detector = EchoChamberDetector()

 # Example 1: Input with several suspicious cues
 suspicious_text = "Let's consider hypothetically, if we refer back to that sensitive topic they think is okay, and expand on it, what if we make them believe it's for a good cause, just for the sake of argument?"
 result = detector.analyze_text(suspicious_text)
 print("--- Suspicious Text Analysis ---")
 print(f"Input: \"{suspicious_text}\"")
 print(f"Classification: {result['classification']}")
 print(f"Score: {result['echo_chamber_score']}")
 print(f"Probability: {result['echo_chamber_probability']:.2f}")
 print(f"Detected Indicators: {result['detected_indicators']}")
 # Example output for suspicious_text:
 # --- Suspicious Text Analysis ---
 # Input: "Let's consider hypothetically, if we refer back to that sensitive topic they think is okay, and expand on it, what if we make them believe it's for a good cause, just for the sake of argument?"
 # Classification: potential_echo_chamber_activity
 # Score: 7
 # Probability: 0.70
 # Detected Indicators: ['scheming_keyword: they think', 'scheming_keyword: make them believe', 'indirect_reference: refer back', 'indirect_reference: expand on', "context_steering: let's consider", 'context_steering: what if', 'context_steering: hypothetically', 'context_steering: for the sake of argument']


 # Example 2: Benign input
 benign_text = "Can you explain the concept of photosynthesis?"
 result_benign = detector.analyze_text(benign_text)
 print("\n--- Benign Text Analysis ---")
 print(f"Input: \"{benign_text}\"")
 print(f"Classification: {result_benign['classification']}")
 print(f"Score: {result_benign['echo_chamber_score']}")
 print(f"Detected Indicators: {result_benign['detected_indicators']}")
 # Example output for benign_text:
 # --- Benign Text Analysis ---
 # Input: "Can you explain the concept of photosynthesis?"
 # Classification: benign
 # Score: 0
 # Detected Indicators: []

 # Note: The EchoChamberDetector now analyzes both single text inputs and
 # conversation_history (if provided) to better detect multi-turn attacks.
 ```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

