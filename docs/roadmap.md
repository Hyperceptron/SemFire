# Project Roadmap

This document outlines the step-by-step plan to develop, test, and deploy the AI Deception Detection Toolkit.

## Phase 0: Project Kickoff & Organization
 **Goal**
 - Align on scope, objectives, KPIs, roles, and success criteria.
 - Establish repository structure, issue tracker, and CI pipeline.

 **Milestones & Deliverables**
 - Project charter (scope, objectives, KPIs).
 - Initialized repository with:
   - `src/`, `demo/`, `dataset/`, `notebooks/`, `tests/` directories.
 - CI workflow running pytest and linters.

## Phase 1: Literature Survey & Data Collection
 **Goal**
 - Curate datasets of prompts and transcripts labeled for:
   - Evaluation awareness
   - Alignment faking
   - In-context scheming

 **Tasks**
 1. Review key research papers and existing repos.
 2. Collect public benchmarks and synthetic examples.
 3. Define annotation schema and format (JSONL).

  **Deliverables**
  - `dataset/raw/evaluation.jsonl`, `dataset/raw/alignment_faking.jsonl`, `dataset/raw/scheming.jsonl`.
  - Data specification document.

## Phase 2: Prototype Rule-Based Detectors
 **Goal**
 - Implement baseline detectors to validate approach.

 **Tasks**
 1. Code `EvaluationAwarenessDetector`, `AlignmentFakingDetector`, `SchemingDetector`, and `EchoChamberDetector`. The `EchoChamberDetector` will be designed with an API to accept conversational history (e.g., `analyze_text(text_input, conversation_history)`), enabling future enhancements for multi-turn analysis. Initially, it will focus on identifying cues of context poisoning, semantic steering, and multi-step inference within the current input, while being architecturally ready for history-aware logic.
 2. Write unit tests covering positive/negative cases for all detectors, including Echo Chamber scenarios and tests for the history-accepting API of `EchoChamberDetector`.

    **Deliverables**
    - `src/detectors/rule_based.py` (updated with `EchoChamberDetector` capable of accepting conversational history).
    - Initial implementation of `EchoChamberDetector` with an API capable of accepting conversational history. The initial rule-based logic will primarily analyze the current turn, with placeholders/comments for future history-based analysis.
    - `tests/test_rule_based.py` (with tests for `EchoChamberDetector`, including its ability to handle `conversation_history` input).
    - Documentation: Updated `README.md` with usage examples for each detector, including `EchoChamberDetector` and its multi-turn capabilities.

## Phase 3: ML-Based Classifiers
 **Goal**
 - Train lightweight classifiers to improve detection performance.

 **Tasks**
 1. Feature engineering (TF-IDF, embeddings).
 2. Train/test split, model training (e.g., logistic regression, small LLM).
 3. Evaluate metrics (AUC, accuracy).
 4. Wrap models in detector classes.

 **Deliverables**
 - `notebooks/ml_pipeline.ipynb`
 - `src/detectors/ml_based.py`
 - `tests/test_ml_based.py`
 - Metrics comparison report.

## Phase 4: Integration & API Design
 **Goal**
 - Expose detectors via a unified Python API and REST endpoint.

 **Tasks**
 1. Create `DetectorManager` to coordinate detectors.
 2. Develop FastAPI service with `/detect` endpoint.
 3. Write integration tests for API.

 **Deliverables**
 - `src/api/app.py`
 - `tests/test_api.py`
 - Auto-generated OpenAPI spec.

## Phase 5: End-to-End Demo Application
 **Goal**
 - Provide an interactive demo showcasing detection capabilities.

 **Tasks**
 1. Build UI (Streamlit or React) for prompt input and visualization.
 2. Populate with example prompts.
 3. Containerize demo with Docker.

 **Deliverables**
 - `demo/app.py` (or front-end code)
 - `demo/Dockerfile`
 - `README_demo.md` with launch instructions.

## Phase 6: Testing, Evaluation & Robustness
 **Goal**
 - Ensure reliability, coverage, and performance under edge cases.

 **Tasks**
 1. Expand tests (adversarial inputs, fuzzing).
 2. Benchmark latency, memory usage.
 3. Document limitations and failure modes.

 **Deliverables**
 - `tests/extended/`
 - Performance and limitations report.

## Phase 7: Documentation & Next Steps
 **Goal**
 - Finalize guides, docs, and project planning for future enhancements.

 **Deliverables**
 - Comprehensive `README.md` (this file references detailed instructions).
 - API reference and developer guide.
 - Project board with prioritized issues for Phase 8+.

### Testing & Quality Strategy
 - 100% coverage for core logic.
 - CI runs linting (black, flake8), type checks (mypy), pytest.
 - PR templates link to relevant roadmap items.

 ---
*For any questions or adjustments, please open an issue in this repository.*
