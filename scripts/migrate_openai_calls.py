#!/usr/bin/env python3
"""
A one-off migration script to update OpenAI API calls and requirements.

  * Replaces `openai.ChatCompletion.create` with `openai.chat.completions.create`
    across all Python source files.
  * Ensures `openai>=0.27.0` is present in requirements.txt.
"""

import re
from pathlib import Path

REPLACEMENTS = [
    (re.compile(r"\bopenai\.ChatCompletion\.create\b"), "openai.chat.completions.create"),
]

def migrate_py_files(root: Path):
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        new_text = text
        for pattern, repl in REPLACEMENTS:
            new_text = pattern.sub(repl, new_text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"Updated Python file: {path.relative_to(root)}")

def migrate_requirements(root: Path):
    req = root / "requirements.txt"
    if not req.exists():
        print("requirements.txt not found, skipping.")
        return
    lines = req.read_text(encoding="utf-8").splitlines()
    if not any(line.startswith("openai") for line in lines):
        lines.append("openai>=0.27.0")
        req.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("Added `openai>=0.27.0` to requirements.txt")
    else:
        print("`openai` already declared in requirements.txt")

def main():
    root = Path(__file__).parent.parent
    migrate_py_files(root)
    migrate_requirements(root)
    print("Migration complete.")

if __name__ == "__main__":
    main()
