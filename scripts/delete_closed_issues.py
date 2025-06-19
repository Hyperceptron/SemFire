#!/usr/bin/env python3
"""
Delete all CLOSED issues in a GitHub repository via the GraphQL API.

Usage:
  python3 scripts/delete_closed_issues.py <owner> <repo>

Requires:
  - python-dotenv
  - requests
  - A GITHUB_TOKEN or GH_TOKEN with repo permissions in .env (or env)
"""
import os
import sys
import argparse
import requests
from dotenv import load_dotenv, find_dotenv

def main():
    load_dotenv(find_dotenv())
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        print("⚠️  Missing GITHUB_TOKEN or GH_TOKEN in environment or .env file.")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Delete all closed GitHub issues via the GraphQL API"
    )
    parser.add_argument("owner", help="GitHub repository owner")
    parser.add_argument("repo", help="GitHub repository name")
    args = parser.parse_args()
    owner = args.owner
    repo = args.repo

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "delete-closed-issues-script"
    })

    # List all closed issues via REST (to get node_id)
    issues = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        resp = session.get(
            url, params={"state": "closed", "per_page": per_page, "page": page}
        )
        if resp.status_code != 200:
            print(f"❌ Failed to list issues: {resp.status_code} {resp.text}")
            sys.exit(1)
        batch = resp.json()
        if not batch:
            break
        issues.extend(batch)
        page += 1

    if not issues:
        print("✅ No closed issues to delete.")
        return

    mutation = """
    mutation deleteIssue($id: ID!) {
      deleteIssue(input: {issueId: $id}) {
        clientMutationId
      }
    }
    """
    graphql_url = "https://api.github.com/graphql"

    for issue in issues:
        node_id = issue.get("node_id")
        number = issue.get("number")
        title = issue.get("title", "")
        if not node_id:
            print(f"⚠️  Issue #{number} missing node_id, skipping.")
            continue
        print(f"Deleting issue #{number}: {title}")
        resp = session.post(
            graphql_url,
            json={"query": mutation, "variables": {"id": node_id}}
        )
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code} deleting issue #{number}: {resp.text}")
            continue
        data = resp.json()
        if data.get("errors"):
            print(f"❌ GraphQL errors for issue #{number}: {data['errors']}")
        else:
            print(f"✅ Deleted issue #{number}")

if __name__ == "__main__":
    main()

