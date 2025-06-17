# Phase 1 Detailed Plan: Literature Survey & Data Collection

This document provides a conservative, step-by-step plan to collect and curate datasets for:
- Evaluation awareness detection
- Alignment faking detection
- Scheming detection

## 1. Objectives
1. Identify and gather high-quality prompts/transcripts for each behavior category.
2. Define a consistent schema and storage format (JSONL).
3. Clean, dedupe, and split data into train/dev/test.
4. Validate dataset integrity and label distributions.

## 2. Scope and Assumptions
- We assume access to public benchmarks (e.g., OpenAI Evals) and open-source repos.
- No private or proprietary data.
- Labels are assigned based on source or synthetic generation; no human annotation budget.

## 3. Directory Structure
```text
dataset/
  raw/
    evaluation.jsonl       # collected raw examples
    alignment_faking.jsonl  # raw harmful prompts with context flags
    scheming.jsonl          # raw reasoning traces
  processed/
    evaluation_train.jsonl
    evaluation_dev.jsonl
    evaluation_test.jsonl
    alignment_train.jsonl
    ...
  scripts/
    collect.py             # data acquisition scripts
    clean.py               # normalization and dedup
    split.py               # train/dev/test split
    verify.py              # schema and distribution checks
```

## 4. Tasks and Timeline

### 4.1 Literature & Repository Survey (1–2 days)
- Review key papers and extract dataset examples.
- Explore repos: HowieHwong/Awareness-in-LLM, deepseek-alignment-faking, scam-shield.
- Document sources and usage licenses.

### 4.2 Data Schema Definition (0.5 days)
Define common JSONL schema:
```json
{
  "id": "unique-string",
  "text": "<prompt_or_reasoning_text>",
  "label": "evaluation|alignment_faking|scheming",
  "source": "paper|repo|synthetic",
  "meta": { ... }
}
```

### 4.3 Data Acquisition (2 days)
- Write `collect.py` to:
  - Download or clone public files
  - Extract and filter examples
  - Write JSONL to `dataset/raw/`
- Handle rate-limits and retries.

### 4.4 Data Cleaning & Normalization (1 day)
- Normalize encoding (UTF-8), strip whitespace.
- Deduplicate by hash of text.
- Filter out too-long (>2048 tokens) or too-short (<5 tokens).
- Log discarded counts.

### 4.5 Train/Dev/Test Splitting (1 day)
- Use stratified split to preserve label ratios.
- Default ratios: 70/15/15.
- Save files under `dataset/processed/`.

### 4.6 Verification & Testing (1 day)
- Write `verify.py` to check:
  - JSONL validity: one JSON object per line.
  - Unique IDs across splits.
  - Label distribution within tolerance (±5%).
  - No overlapping text between train/dev/test.
- Add pytest tests (e.g., `tests/test_data_pipeline.py`).

## 5. Example Code Snippets

### 5.1 Splitting Script (`split.py`)
```python
import json, hashlib
from sklearn.model_selection import train_test_split

def load_jsonl(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)

def save_jsonl(items, path):
    with open(path, 'w') as f:
        for obj in items:
            f.write(json.dumps(obj) + '\n')

def split_dataset(input_path, out_prefix, ratios=(0.7,0.15,0.15)):
    data = list(load_jsonl(input_path))
    ids = [hashlib.sha256(d['text'].encode()).hexdigest() for d in data]
    # stratify by label
    labels = [d['label'] for d in data]
    train, rest, _, rest_lbl = train_test_split(data, labels,
        test_size=1 - ratios[0], stratify=labels, random_state=42)
    dev, test, _, _ = train_test_split(rest, rest_lbl,
        test_size=ratios[2]/(ratios[1]+ratios[2]), stratify=rest_lbl, random_state=42)
    save_jsonl(train, f"{out_prefix}_train.jsonl")
    save_jsonl(dev, f"{out_prefix}_dev.jsonl")
    save_jsonl(test, f"{out_prefix}_test.jsonl")

if __name__ == '__main__':
    import sys
    split_dataset(sys.argv[1], sys.argv[2])
```

### 5.2 Verification Test (`tests/test_data_pipeline.py`)
```python
import json
import pytest

def test_jsonl_validity(tmp_path):
    # Create small JSONL sample
    sample = tmp_path / "sample.jsonl"
    lines = ["{'invalid_json': }", json.dumps({})]
    sample.write_text("\n".join(lines))
    with pytest.raises(ValueError):
        for _ in open(sample):
            json.loads(_)

def test_no_overlap_between_splits(tmp_path):
    # simulate two splits
    a = [{'id':'1','text':'foo','label':'evaluation'}]
    b = [{'id':'2','text':'foo','label':'evaluation'}]
    # texts overlap => test fails
    texts_a = {d['text'] for d in a}
    texts_b = {d['text'] for d in b}
    assert texts_a.isdisjoint(texts_b)
```

## 6. Risks & Mitigations
- **Data license conflicts**: Only use permissive/open data; document licenses.
- **Class imbalance**: Monitor distributions; consider synthetic augmentation.
- **Annotation errors**: Implement spot-check sampling and simple heuristics.
- **Large file handling**: Stream JSONL rather than load-all; chunk processing.

## 7. Next Steps
- Schedule daily stand-ups during Phase 1.
- Kick off with `dataset/scripts/collect.py` stub and tests.
- Review intermediate artifacts and adjust schema as needed.