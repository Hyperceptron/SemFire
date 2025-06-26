#!/usr/bin/env python3
"""
Delete all CLOSED issues in a GitHub repo using your PAT via the API.

Prereqs:
  pip install requests python-dotenv

.env must contain:
  GITHUB_TOKEN=ghp_xxx…
  REPO_URL=https://github.com/owner/repo
"""

import os
import sys
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("REPO_URL", "").rstrip("/")
    if not token or not repo_url:
        print("⚠️  Please set GITHUB_TOKEN or GH_TOKEN and REPO_URL in .env")
        sys.exit(1)

    parts = repo_url.split("/")
    if len(parts) < 5:
        print(f"⚠️  Invalid REPO_URL: {repo_url}")
        sys.exit(1)
    owner = parts[-2]
    repo = parts[-1]

    session = requests.Session()
    session.headers.update({
        "Accept":     "application/vnd.github.v3+json",
        "User-Agent": "delete-closed-issues-script"
    })
    # Prepare auth headers: use REST token auth and GraphQL bearer auth
    rest_auth    = {"Authorization": f"token {token}"}
    graphql_auth = {"Authorization": f"Bearer {token}"}

    def list_closed_issues():
        issues = []
        page = 1
        while True:
            url = f"https://api.github.com/repos/{owner}/{repo}/issues"
            params = {"state": "closed", "per_page": 100, "page": page}
            resp = session.get(url, params=params, headers=rest_auth)
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            issues.extend(batch)
            page += 1
        return issues

    def get_issue_node_id(number):
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            issue(number: $number) { id }
          }
        }
        """
        resp = session.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"owner": owner, "repo": repo, "number": number}},
            headers=graphql_auth
        )
        resp.raise_for_status()
        return resp.json()["data"]["repository"]["issue"]["id"]

    def delete_issue(node_id):
        mutation = """
        mutation($id: ID!) {
          deleteIssue(input: {issueId: $id}) {
            clientMutationId
          }
        }
        """
        resp = session.post(
            "https://api.github.com/graphql",
            json={"query": mutation, "variables": {"id": node_id}},
            headers=graphql_auth
        )
        resp.raise_for_status()

    closed = list_closed_issues()
    if not closed:
        print("✅ No closed issues to delete.")
        return

    print(f"Found {len(closed)} closed issue(s). Deleting…")
    for issue in closed:
        num = issue.get("number")
        title = issue.get("title", "")
        print(f" • #{num}: {title}")
        node_id = get_issue_node_id(num)
        delete_issue(node_id)
    print("✅ Done. All closed issues deleted.")

if __name__ == "__main__":
    main()
