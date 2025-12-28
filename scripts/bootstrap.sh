#!/bin/bash
# Bootstrap script: Verify prerequisites for release PR workflow

set -euo pipefail

echo "🔍 Checking prerequisites..."

# Check git
if ! command -v git &> /dev/null; then
    echo "❌ git is not installed. Please install git first."
    exit 1
fi
echo "✅ git found: $(git --version)"

# Check gh
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install from: https://cli.github.com/"
    exit 1
fi
echo "✅ gh found: $(gh --version | head -n 1)"

# Check gh auth
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI is not authenticated."
    echo "   Run: gh auth login"
    exit 1
fi
echo "✅ GitHub CLI authenticated"

# Check we're in a git repo
if ! git rev-parse --git-dir &> /dev/null; then
    echo "❌ Not in a git repository."
    exit 1
fi
echo "✅ In git repository"

# Check repo.config.json exists
if [ ! -f "repo.config.json" ]; then
    echo "❌ repo.config.json not found in current directory."
    exit 1
fi
echo "✅ repo.config.json found"

echo ""
echo "✅ All prerequisites met!"
echo ""
echo "Next steps:"
echo "  make verify  - Run quality gates"
echo "  make pr      - Create release PR"

