#!/usr/bin/env bash
set -euo pipefail

# Permanently delete all closed issues in josephedward/R.A.D.A.R.
export GH_TOKEN="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"

owner="josephedward"
repo="R.A.D.A.R."
cursor="null"

while :; do
  resp=$(gh api graphql -f owner="$owner" -f name="$repo" -f cursor="$cursor" << 'GRAPHQL'
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 100, after: $cursor, states: CLOSED) {
      pageInfo { hasNextPage endCursor }
      nodes { id }
    }
  }
}
GRAPHQL
  )

  ids=( $(jq -r '.data.repository.issues.nodes[].id' <<< "$resp") )
  if [ ${#ids[@]} -eq 0 ]; then
    echo "✅ No more closed issues to delete."
    break
  fi

  for id in "${ids[@]}"; do
    gh api graphql -f query="mutation { deleteIssue(input:{issueId: \"$id\"}) { clientMutationId } }"
    echo "🗑 Deleted issue $id"
  done

  hasNext=$(jq -r '.data.repository.issues.pageInfo.hasNextPage' <<< "$resp")
  if [ "$hasNext" != "true" ]; then
    echo "✅ Finished deleting all closed issues."
    break
  fi
  cursor=$(jq -r '.data.repository.issues.pageInfo.endCursor' <<< "$resp")
done
