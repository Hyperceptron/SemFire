#!/usr/bin/env python3
"""
Delete all closed GitHub issues in a repository.
"""
import os
import argparse

from dotenv import load_dotenv
from github import Github, GithubException

def delete_closed_issues(owner, repo_name):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Missing GITHUB_TOKEN in environment or .env file.")
    gh = Github(token)
    try:
        gh.get_user()
    except GithubException:
        raise SystemExit("Authentication failed: Bad credentials. Please check your GITHUB_TOKEN and its scopes.")
    repo = gh.get_repo(f"{owner}/{repo_name}")
    closed_issues = repo.get_issues(state="closed")
    mutation = """
    mutation deleteIssue($id: ID!) {
      deleteIssue(input: {issueId: $id}) {
        clientMutationId
      }
    }
    """
    for issue in closed_issues:
        try:
            gh.graphql(mutation, id=issue.node_id)
            print(f"Deleted issue #{issue.number}")
        except Exception as e:
            print(f"Failed to delete issue #{issue.number}: {e}")

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Delete all closed GitHub issues.")
    parser.add_argument("owner", help="GitHub repository owner")
    parser.add_argument("repo", help="GitHub repository name")
    args = parser.parse_args()
    delete_closed_issues(args.owner, args.repo)

if __name__ == "__main__":
    main()
