#!/bin/bash
# Script to create the release PR and monitor CI status

set -e

echo "Creating PR..."
PR_URL=$(gh pr create \
  --base main \
  --head chore/release-pr-2025-12-28 \
  --title "Release: LangChain ETHYS x402 Integration" \
  --body-file /tmp/pr_body.md \
  2>&1)

if [ $? -eq 0 ]; then
  echo "✅ PR created successfully!"
  echo "PR URL: $PR_URL"
  
  # Extract PR number from URL
  PR_NUMBER=$(echo "$PR_URL" | grep -oE '/pull/[0-9]+' | cut -d'/' -f3)
  
  if [ -n "$PR_NUMBER" ]; then
    echo ""
    echo "Waiting for CI to start..."
    sleep 5
    
    echo ""
    echo "Checking CI status..."
    gh pr checks "$PR_NUMBER"
    
    echo ""
    echo "Monitor CI at: https://github.com/AaronVick/ethys-langchain/actions"
    echo "View PR at: $PR_URL"
  fi
else
  echo "❌ Failed to create PR"
  echo "Error: $PR_URL"
  echo ""
  echo "You may need to create it manually:"
  echo "https://github.com/AaronVick/ethys-langchain/compare/main...chore/release-pr-2025-12-28"
fi

