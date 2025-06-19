#!/usr/bin/env python3
"""
Delete all closed issues in a GitHub repository via the GraphQL API.

Usage:
  python3 scripts/delete_closed_issues_api.py <owner> <repo>

Requires:
  - python-dotenv
  - requests
  - A GITHUB_TOKEN or GH_TOKEN with admin/delete-issues permissions in .env or env
"""
import os
import sys
import requests
from dotenv import load_dotenv, find_dotenv

def fetch_closed_issue_ids(session, graphql_url, owner, repo):
    query = """
    query ($owner: String!, $repo: String!, $after: String) {
      repository(owner: $owner, name: $repo) {
        issues(first: 100, states: CLOSED, after: $after) {
          pageInfo { hasNextPage endCursor }
          nodes { id number title }
        }
      }
    }
    """
    cursor = None
    while True:
        resp = session.post(
            graphql_url,
            json={"query": query, "variables": {"owner": owner, "repo": repo, "after": cursor}}
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errors"):
            print("❌ Error fetching issues:", data["errors"])
            sys.exit(1)
        issues = data["data"]["repository"]["issues"]["nodes"]
        for issue in issues:
            yield issue
        page_info = data["data"]["repository"]["issues"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

def delete_issue(session, graphql_url, issue_id, number, title):
    mutation = """
    mutation($id: ID!) {
      deleteIssue(input: {issueId: $id}) {
        clientMutationId
      }
    }
    """
    resp = session.post(
        graphql_url,
        json={"query": mutation, "variables": {"id": issue_id}}
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        print(f"❌ GraphQL errors deleting issue #{number}: {data['errors']}")
    else:
        print(f"✅ Deleted issue #{number}: {title}")

def main():
    load_dotenv(find_dotenv())
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        print("⚠️  Missing GITHUB_TOKEN or GH_TOKEN.")
        sys.exit(1)
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/delete_closed_issues_api.py <owner> <repo>")
        sys.exit(1)
    owner, repo = sys.argv[1], sys.argv[2]
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    graphql_url = "https://api.github.com/graphql"
    for issue in fetch_closed_issue_ids(session, graphql_url, owner, repo):
        delete_issue(session, graphql_url, issue["id"], issue["number"], issue.get("title", ""))

if __name__ == "__main__":
    main()
