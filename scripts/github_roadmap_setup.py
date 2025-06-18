#!/usr/bin/env python3
"""
Automate GitHub milestones and issues from ROADMAP.md.
"""
import os
import re
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def parse_roadmap(path="ROADMAP.md"):  # noqa: C901
    issues = []
    current_ms = None
    phase_header = re.compile(r"^\s*##\s*Phase\s*(\d+):\s*(.+)$")
    tasks_heading = re.compile(r"^\*\*Tasks\*\*")
    section_heading = re.compile(r"^\*\*(.+)\*\*")
    bullet_pattern = re.compile(r"^\s*(?:-|\d+\.)\s+(.+)$")
    inside_tasks = False
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()
                m_phase = phase_header.match(line)
                if m_phase:
                    num, desc = m_phase.group(1), m_phase.group(2).strip()
                    current_ms = f"Phase {num}: {desc}"
                    inside_tasks = False
                    continue
                if tasks_heading.match(line.strip()):
                    inside_tasks = True
                    continue
                if section_heading.match(line.strip()) and not tasks_heading.match(line.strip()):
                    inside_tasks = False
                    continue
                if inside_tasks:
                    m_b = bullet_pattern.match(line)
                    if m_b and current_ms:
                        issues.append({"title": m_b.group(1).strip(), "milestone": current_ms})
    except FileNotFoundError:
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    return issues

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create GitHub milestones and issues from ROADMAP.md")
    parser.add_argument("--repo", help="GitHub repo in owner/name format")
    parser.add_argument("--dry-run", action="store_true", help="Print gh CLI commands without executing")
    parser.add_argument("--path", default="ROADMAP.md", help="Path to ROADMAP.md")
    args = parser.parse_args()

    repo_name = args.repo or os.getenv("GITHUB_REPO")
    if not repo_name:
        repo_name = input("Repository (owner/name): ").strip()

    issues = parse_roadmap(args.path)
    milestones = sorted({item["milestone"] for item in issues if item.get("milestone")})

    if args.dry_run:
        for ms in milestones:
            print(f"gh milestone create --repo {repo_name} --title \"{ms}\"")
        for item in issues:
            cmd = f"gh issue create --repo {repo_name} --title \"{item['title']}\""
            if item.get("milestone"):
                cmd += f" --milestone \"{item['milestone']}\""
            print(cmd)
        return

    try:
        from github import Github
        from github.GithubException import GithubException
    except ImportError:
        print("Error: PyGithub not installed. Install with `pip install PyGithub`", file=sys.stderr)
        sys.exit(1)

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    gh = Github(token)
    try:
        repo = gh.get_repo(repo_name)
    except GithubException as e:
        print(f"Error: cannot access repository {repo_name}: {e}", file=sys.stderr)
        sys.exit(1)

    existing_ms = {m.title: m for m in repo.get_milestones(state="all")}
    for ms_title in milestones:
        if ms_title not in existing_ms:
            print(f"Creating milestone: {ms_title}")
            try:
                m = repo.create_milestone(title=ms_title)
                existing_ms[ms_title] = m
            except GithubException as e:
                print(f"Warning: could not create milestone {ms_title}: {e}", file=sys.stderr)

    existing_titles = {i.title for i in repo.get_issues(state="all")}
    for item in issues:
        title = item["title"]
        if title in existing_titles:
            print(f"Skipping existing issue: {title}")
            continue
        kwargs = {"title": title}
        ms = item.get("milestone")
        if ms and ms in existing_ms:
            kwargs["milestone"] = existing_ms[ms]
        print(f"Creating issue: {title}")
        try:
            repo.create_issue(**kwargs)
        except GithubException as e:
            print(f"Warning: could not create issue {title}: {e}", file=sys.stderr)

    print("Done.")

if __name__ == "__main__":
    main()