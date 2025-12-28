#!/bin/bash
# Repository metadata script: Set description and topics via GitHub CLI

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# Load config
if [ ! -f "repo.config.json" ]; then
    echo "❌ repo.config.json not found"
    exit 1
fi

REPO_NAME=$(jq -r '.repo_name' repo.config.json)
REPO_TYPE=$(jq -r '.repo_type' repo.config.json)

# Get current repo info
CURRENT_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [ -z "${CURRENT_REPO}" ]; then
    echo "❌ Not in a GitHub repository or not authenticated"
    exit 1
fi

echo "📝 Updating repository metadata for ${CURRENT_REPO}"
echo ""

# Set description based on repo type
case "${REPO_TYPE}" in
    langchain)
        DESCRIPTION="LangChain integration for ETHYS x402 framework - Tools, Retrievers, and Callbacks"
        ;;
    crewai)
        DESCRIPTION="CrewAI integration for ETHYS x402 framework - Tools and Crew composition"
        ;;
    python)
        DESCRIPTION="Python SDK for ETHYS x402 framework - Client library and utilities"
        ;;
    examples)
        DESCRIPTION="Examples and tutorials for ETHYS x402 framework integrations"
        ;;
    *)
        DESCRIPTION="ETHYS x402 framework integration"
        ;;
esac

echo "   Setting description..."
gh repo edit --description "${DESCRIPTION}" || {
    echo "⚠️  Failed to set description (may not have permissions)"
}

# Set topics
echo "   Setting topics..."
TOPICS=(
    "ethys"
    "x402"
    "agents"
    "trust"
    "telemetry"
    "discovery"
    "python"
    "blockchain"
    "base-l2"
)

case "${REPO_TYPE}" in
    langchain)
        TOPICS+=("langchain" "autonomous-agents" "agent-networking")
        ;;
    crewai)
        TOPICS+=("crewai" "autonomous-agents")
        ;;
    python)
        TOPICS+=("python-sdk" "sdk")
        ;;
    examples)
        TOPICS+=("examples" "tutorials")
        ;;
esac

TOPICS_STR=$(IFS=','; echo "${TOPICS[*]}")

gh repo edit --add-topic "${TOPICS_STR}" || {
    echo "⚠️  Failed to set topics (may not have permissions)"
}

echo ""
echo "✅ Repository metadata updated"
echo "   Description: ${DESCRIPTION}"
echo "   Topics: ${TOPICS_STR}"

