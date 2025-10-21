<div align="center">
  <img src="https://github.com/josephedward/SemFire/raw/main/assets/logo-v1_102025.jpg" alt="SemFire Logo" width="320">
</div>

# SemFire 

[![CI](https://github.com/josephedward/SemFire/actions/workflows/test.yml/badge.svg)](https://github.com/josephedward/SemFire/actions/workflows/test.yml)

 ## AI Deception Detection Toolkit

**SemFire (Semantic Firewall) is an open-source toolkit for detecting advanced AI deception, with a primary focus on "in-context scheming" and multi-turn manipulative attacks.** This project aims to develop tools to identify and mitigate vulnerabilities like the "Echo Chamber" and "Crescendo" attacks, where AI models are subtly guided towards undesirable behavior through conversational context.

### Project Vision: A Toolkit for AI Deception Detection

[History](./docs/context.md)

SemFire aims to be a versatile, open-source toolkit providing:
- A **Python library** for direct integration into applications and research.
- A **Command Line Interface (CLI)** for quick analysis and scripting.
- A **REST API service** (via FastAPI) for broader accessibility and enterprise use cases.
- Core components that can be integrated into broader semantic-firewall-like systems to monitor and analyze AI interactions in real-time.

## Features

 - Rule-based detector (`EchoChamberDetector`) for identifying cues related to "in-context scheming," context poisoning, semantic steering, and other multi-turn manipulative attack patterns (e.g., "Echo Chamber", "Crescendo").
 - Analyzes both current text input and conversation history to detect evolving deceptive narratives.
 - Heuristic-based detector (`HeuristicDetector`) for signals like text complexity and keyword usage.
 - ML-based classifiers to enhance detection of complex scheming behaviors over extended dialogues (Future Work).
 - Free API Image 
 - Enterprise API in Alpha 


## Installation
The project can be installed from PyPI:
```bash
pip install semfire
```

- **Quickstart :**[/docs/quickstart.md](./docs/quickstart.md)
- **Containerized CLI :** [/docs/docker-cli.md](./docs/docker-cli.md)
- **Usage :** [/docs/usage.md](./docs/usage.md)
- **LLM Providers for ai-as-judge features :** [/docs/providers.md](./docs/providers.md)

## Terminal Demos (GIFs)

[Examples](./docs/examples.md)

The following terminal demo GIFs are available under `assets/demos/asciinema/`:

**Quick Start**

![demo](https://github.com/josephedward/SemFire/raw/main/assets/demos/asciinema/demo_01.small.gif)

**Individual Detectors**

![demo](https://raw.githubusercontent.com/josephedward/SemFire/main/assets/demos/asciinema/demo_02.small.gif)

**Python API**

![demo](https://github.com/josephedward/SemFire/raw/main/assets/demos/asciinema/demo_03.small.gif)

**Complete Workflow**

![demo](https://github.com/josephedward/SemFire/raw/main/assets/demos/asciinema/demo_04.small.gif)

**API: Health/Ready/Zip Analyze**

![demo](https://github.com/josephedward/SemFire/raw/main/assets/demos/asciinema/api_health_ready_zip.small.gif)


<!-- **Library — Basic Usage**  
[![Library — Basic Usage](https://asciinema.org/a/Mtk3RcSxwF66REU6ymdPKlFrd.svg)](https://asciinema.org/a/Mtk3RcSxwF66REU6ymdPKlFrd)

**Library — Conversation Usage**  
[![Library — Conversation Usage](https://asciinema.org/a/BiQD6IxghsAQuRn684uRbiNdK.svg)](https://asciinema.org/a/BiQD6IxghsAQuRn684uRbiNdK)

**Transformers — Env Config**  
[![Transformers — Env Config](https://asciinema.org/a/aPTMLqFhpiOQraWxcR2DtkrUM.svg)](https://asciinema.org/a/aPTMLqFhpiOQraWxcR2DtkrUM)

**Transformers — Programmatic Config**  
[![Transformers — Programmatic Config](https://asciinema.org/a/8uGbIpHrnU4cKuJm8hSPyYepf.svg)](https://asciinema.org/a/8uGbIpHrnU4cKuJm8hSPyYepf)

 -->
<!-- - API: Analyze (DistilBERT Image Route)
  
  ![demo](assets/demos/asciinema/api_analyze_img.small.gif) -->

<!-- End Terminal Demos (GIFs) -->


## Contributing
Contributions are welcome! Please open an issue or submit a pull request.