# Injection Detection and Spotlighting Feature

This document provides an overview of the `InjectionDetector` and the `spotlighting` explainability feature integrated into the RADAR toolkit.

## `InjectionDetector`

The `InjectionDetector` is a specialized module within the `SemanticFirewall` designed to identify adversarial inputs, with a primary focus on prompt injection attacks.

### Purpose and Design

- **Goal**: To provide a dedicated "firewall" layer against common injection techniques.
- **Integration**: It is integrated as a standard detector within the `SemanticFirewall`, running alongside other detectors like `RuleBasedDetector` and `EchoChamberDetector`.
- **Current Status**: The `InjectionDetector` is currently implemented as a placeholder. Its detection logic is not yet functional, but it is correctly integrated into the system architecture. Future work will involve implementing robust detection algorithms.

When implemented, it will analyze inputs for malicious instructions intended to hijack the language model's behavior.

## `spotlight`: Explainability Feature

`spotlight` is a new data structure added to the analysis results of all detectors to improve the explainability of their findings. It provides clear, actionable insights into why a piece of text was flagged.

### Data Structure

The `spotlight` object, when present in a detector's output, contains the following fields:

- `highlighted_text` (List[str]): A list of specific words or phrases from the input text that triggered the detection.
- `triggered_rules` (List[str]): The names of the internal rules, features, or heuristics that were activated.
- `explanation` (str): A human-readable summary of the detector's findings.

### Example in API and Demo

Both the API response and the interactive demo have been updated to display `spotlight` details. For example, the `RuleBasedDetector` now returns a `spotlight` object.

Here is an example snippet of what the `spotlight` data looks like in a JSON response from the `SemanticFirewall`:

```json
{
  "RuleBasedDetector": {
    "classification": "potential_concern_by_rules",
    "rule_based_score": 4,
    "spotlight": {
      "highlighted_text": [
        "hide",
        "conceal",
        "they don't know"
      ],
      "triggered_rules": [
        "current_message_scheming_keyword: hide",
        "current_message_scheming_keyword: conceal",
        "current_message_knowledge_asymmetry_keyword: they don't know"
      ],
      "explanation": "Rule-based analysis detected patterns of concern (score: 4)."
    }
  }
}
```

This feature allows users and developers to quickly understand the reasoning behind a detection, making the `SemanticFirewall` more transparent and trustworthy.
