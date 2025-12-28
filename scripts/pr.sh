#!/bin/bash
# Release PR script: Create branch, run tasks, commit, push, open PR

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# Check jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed. Install from: https://stedolan.github.io/jq/"
    exit 1
fi

# Load config
if [ ! -f "repo.config.json" ]; then
    echo "❌ repo.config.json not found"
    exit 1
fi

REPO_NAME=$(jq -r '.repo_name' repo.config.json)
REPO_TYPE=$(jq -r '.repo_type' repo.config.json)
DEFAULT_BRANCH=$(jq -r '.default_branch' repo.config.json)
REVIEWERS=$(jq -r '.reviewers[]?' repo.config.json 2>/dev/null | tr '\n' ' ' || echo "")
LABELS=$(jq -r '.labels[]?' repo.config.json 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")

# Create branch name
BRANCH_DATE=$(date +%Y-%m-%d)
BRANCH_NAME="chore/release-pr-${BRANCH_DATE}"

echo "🚀 Creating release PR for ${REPO_NAME}"
echo "   Type: ${REPO_TYPE}"
echo "   Branch: ${BRANCH_NAME}"
echo ""

# Check if branch already exists
if git show-ref --verify --quiet refs/heads/"${BRANCH_NAME}"; then
    echo "⚠️  Branch ${BRANCH_NAME} already exists. Switching to it..."
    git checkout "${BRANCH_NAME}"
else
    # Ensure we're on default branch
    git checkout "${DEFAULT_BRANCH}"
    git pull origin "${DEFAULT_BRANCH}" || true
    
    # Create branch
    git checkout -b "${BRANCH_NAME}"
fi

echo "📋 Checking required files..."

# Check required files exist
REQUIRED_FILES=$(jq -r '.required_files[]?' repo.config.json)
MISSING_FILES=()

while IFS= read -r file; do
    if [ ! -f "${file}" ]; then
        MISSING_FILES+=("${file}")
    fi
done <<< "${REQUIRED_FILES}"

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo "❌ Missing required files:"
    printf '   - %s\n' "${MISSING_FILES[@]}"
    exit 1
fi

echo "✅ All required files present"

echo ""
echo "🔧 Running quality gates..."

# Run install if command exists
INSTALL_CMD=$(jq -r '.commands.install // empty' repo.config.json)
if [ -n "${INSTALL_CMD}" ]; then
    echo "   Installing dependencies..."
    eval "${INSTALL_CMD}" || {
        echo "❌ Install failed"
        exit 1
    }
fi

# Run lint
LINT_CMD=$(jq -r '.commands.lint // empty' repo.config.json)
if [ -n "${LINT_CMD}" ]; then
    echo "   Running lint..."
    eval "${LINT_CMD}" || {
        echo "❌ Lint failed. Fix errors and try again."
        exit 1
    }
fi

# Run format check
FORMAT_CMD=$(jq -r '.commands.format_check // empty' repo.config.json)
if [ -n "${FORMAT_CMD}" ]; then
    echo "   Checking format..."
    eval "${FORMAT_CMD}" || {
        echo "❌ Format check failed. Run: ruff format ."
        exit 1
    }
fi

# Run typecheck
TYPECHECK_CMD=$(jq -r '.commands.typecheck // empty' repo.config.json)
if [ -n "${TYPECHECK_CMD}" ]; then
    echo "   Running typecheck..."
    eval "${TYPECHECK_CMD}" || {
        echo "❌ Typecheck failed. Fix type errors and try again."
        exit 1
    }
fi

# Run tests
TEST_CMD=$(jq -r '.commands.test // empty' repo.config.json)
if [ -n "${TEST_CMD}" ]; then
    echo "   Running tests..."
    eval "${TEST_CMD}" || {
        echo "❌ Tests failed. Fix test failures and try again."
        exit 1
    }
fi

echo "✅ All quality gates passed"
echo ""

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  No changes to commit. Creating PR with existing state..."
else
    echo "📝 Committing changes..."
    git add -A
    git commit -m "chore: release readiness updates

- Verified required files present
- All quality gates passed
- Ready for release review" || {
        echo "⚠️  No changes to commit (or commit failed)"
    }
fi

# Push branch
echo "📤 Pushing branch..."
git push -u origin "${BRANCH_NAME}" || {
    echo "❌ Failed to push branch"
    exit 1
}

# Generate PR body
PR_BODY=$(cat <<EOF
## Release Readiness: ${REPO_NAME} (${BRANCH_DATE})

### Summary
This PR ensures release readiness by verifying:
- ✅ All required files present
- ✅ Quality gates passed
- ✅ Tests passing

### Quality Gates Passed
- [x] Lint: \`${LINT_CMD}\`
- [x] Format: \`${FORMAT_CMD}\`
- [x] Typecheck: \`${TYPECHECK_CMD}\`
- [x] Tests: \`${TEST_CMD}\`

### Required Files Verified
$(echo "${REQUIRED_FILES}" | sed 's/^/- [x] /')

### How to Test
\`\`\`bash
make verify
\`\`\`

### Notes
- Automated release PR workflow
- All gates must pass before merge
EOF
)

# Create PR
echo "🔨 Creating PR..."
PR_ARGS=(
    --title "Release readiness: ${REPO_NAME} (${BRANCH_DATE})"
    --body "${PR_BODY}"
    --base "${DEFAULT_BRANCH}"
    --head "${BRANCH_NAME}"
)

if [ -n "${LABELS}" ]; then
    PR_ARGS+=(--label "${LABELS}")
fi

if [ -n "${REVIEWERS}" ]; then
    PR_ARGS+=(--reviewer "$(echo ${REVIEWERS} | tr ' ' ',')")
fi

PR_URL=$(gh pr create "${PR_ARGS[@]}" 2>&1) || {
    echo "❌ Failed to create PR"
    echo "Output: ${PR_URL}"
    exit 1
}

echo ""
echo "✅ PR created successfully!"
echo "   ${PR_URL}"
echo ""
echo "Next steps:"
echo "  1. Review the PR"
echo "  2. Merge when ready"

