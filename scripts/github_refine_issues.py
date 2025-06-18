#!/usr/bin/env python3
"""
Refine GitHub issues based on ROADMAP.md.

For each open issue:
  - If its title matches an entry in ROADMAP.md, update its body with context.
  - Otherwise close the issue as obsolete.

Usage:
  GITHUB_TOKEN must be set in env.
  python scripts/github_refine_issues.py --repo owner/name [--dry-run]
"""
import os
import re
import sys
import argparse

try:
    from github import Github, GithubException
except ImportError:
    print("Error: PyGithub not installed. Install with `pip install PyGithub`", file=sys.stderr)
    sys.exit(1)


def parse_roadmap(path="ROADMAP.md"):
    """
    Parse ROADMAP.md and return a mapping:
      { issue_title (str): context (str) }
    """
    mapping = {}
    current_ms = None
    phase_header = re.compile(r"^\s*##\s+Phase\s+\d+:\s+(.+)")
    item_pattern = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            mh = phase_header.match(line)
            if mh:
                current_ms = mh.group(1).strip()
                continue
            im = item_pattern.match(line)
            if im and current_ms:
                title = im.group(1).strip()
                mapping[title] = f"**Milestone**: {current_ms}"
    return mapping


def main():
    parser = argparse.ArgumentParser(description="Refine GitHub issues from ROADMAP.md")
    parser.add_argument("--repo", required=True, help="owner/name of the GitHub repo")
    parser.add_argument("--dry-run", action="store_true", help="print actions without executing")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    gh = Github(token)
    try:
        repo = gh.get_repo(args.repo)
    except GithubException as e:
        print(f"Error: cannot access repository {args.repo}: {e}", file=sys.stderr)
        sys.exit(1)

    roadmap_map = parse_roadmap()

    for issue in repo.get_issues(state="open"):
        ctx = roadmap_map.get(issue.title.strip())
        if ctx:
            if issue.body != ctx:
                print(f"Updating issue: {issue.title}")
                if not args.dry_run:
                    issue.edit(body=ctx)
        else:
            print(f"Closing issue: {issue.title}")
            if not args.dry_run:
                if not args.dry_run:
                    issue.edit(state="closed")


if __name__ == "__main__":
    main()
