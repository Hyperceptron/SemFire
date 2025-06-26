#!/usr/bin/env python3
import os
import sys
import argparse
import requests

GITHUB_API_URL = "https://api.github.com/graphql"

def graphql_request(query, variables):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        sys.exit("Error: Missing GITHUB_TOKEN environment variable")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": query, "variables": variables}
    resp = requests.post(GITHUB_API_URL, json=payload, headers=headers)
    if resp.status_code != 200:
        sys.exit(f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        sys.exit(f"GraphQL errors: {data['errors']}")
    return data["data"]

def fetch_closed_issues(owner, repo):
    query = """
query($owner: String!, $repo: String!, $after: String) {
  repository(owner: $owner, name: $repo) {
    issues(states: CLOSED, first: 100, after: $after) {
      pageInfo { hasNextPage, endCursor }
      nodes { id, number }
    }
  }
}
"""
    issues = []
    after = None
    while True:
        variables = {"owner": owner, "repo": repo, "after": after}
        data = graphql_request(query, variables)
        nodes = data["repository"]["issues"]["nodes"]
        issues.extend(nodes)
        page_info = data["repository"]["issues"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        after = page_info["endCursor"]
    return issues

def delete_issue(issue_id):
    mutation = """
mutation($issueId: ID!) {
  deleteIssue(input: {issueId: $issueId}) {
    clientMutationId
  }
}
"""
    graphql_request(mutation, {"issueId": issue_id})

def main():
    parser = argparse.ArgumentParser(description="Delete all closed GitHub issues in a repository")
    parser.add_argument("owner", help="GitHub owner or organization")
    parser.add_argument("repo", help="GitHub repository name")
    parser.add_argument("--dry-run", action="store_true", help="List closed issues without deleting")
    args = parser.parse_args()

    issues = fetch_closed_issues(args.owner, args.repo)
    if not issues:
        print("No closed issues found.")
        return
    print(f"Found {len(issues)} closed issues:")
    for issue in issues:
        print(f"- #{issue['number']} (node id: {issue['id']})")
    if args.dry_run:
        print("Dry run complete; no issues were deleted.")
        return
    confirm = input("Type 'yes' to delete all of these issues: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return
    for issue in issues:
        delete_issue(issue["id"])
        print(f"Deleted issue #{issue['number']}")
    print("Done.")

if __name__ == "__main__":
    main()