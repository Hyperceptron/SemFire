#!/usr/bin/env python3
"""
Sync GitHub issues against ROADMAP.md:
 - For each open issue, if its title matches a roadmap task and its body is empty,
   populate a stub pointing back to the roadmap.
 - If it does not match any roadmap task, close it as non‐actionable.
"""
import os
import sys
import re
import argparse
from github import Github, GithubException

# Optionally load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def parse_roadmap(path: str) -> set:
    """Extract task titles from ROADMAP.md 'Tasks' sections."""
    titles = set()
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    capture = False
    for line in lines:
        if re.match(r'\s*\*\*Tasks\*\*', line):
            capture = True
            continue
        if capture:
            if re.match(r'\s*$', line) or re.match(r'\s*##\s+', line):
                capture = False
            elif re.match(r'\s*[\-\*\d]', line):
                # Remove bullet or number markers
                text = re.sub(r'^\s*[\-\*\d]+\.*\s*', '', line).strip()
                if text:
                    titles.add(text)
    return titles

def main():
    parser = argparse.ArgumentParser(description="Sync GitHub issues with ROADMAP.md")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--path", default="ROADMAP.md", help="Path to ROADMAP.md")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: set GITHUB_TOKEN in env or .env", file=sys.stderr)
        sys.exit(1)

    roadmap_titles = parse_roadmap(args.path)
    gh = Github(token)
    try:
        repo = gh.get_repo(args.repo)
    except GithubException as e:
        print(f"Error accessing repo {args.repo}: {e}", file=sys.stderr)
        sys.exit(1)

    for issue in repo.get_issues(state="open"):
        title = issue.title.strip()
        if title in roadmap_titles:
            if not issue.body or not issue.body.strip():
                new_body = f"See ROADMAP.md for task details:\n\n- **Task**: {title}"
                issue.edit(body=new_body)
                print(f"Updated body: {title}")
        else:
            issue.create_comment("Closing as this issue is not in the ROADMAP and is non-actionable.")
            issue.edit(state="closed")
            print(f"Closed issue: {title}")

if __name__ == "__main__":
    main()
