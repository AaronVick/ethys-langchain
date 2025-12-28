.PHONY: bootstrap verify pr meta help

help:
	@echo "ETHYS LangChain Release PR Workflow"
	@echo ""
	@echo "Targets:"
	@echo "  make bootstrap  - Verify prerequisites (git, gh, auth)"
	@echo "  make verify     - Run quality gates (lint, format, typecheck, tests)"
	@echo "  make pr         - Create release PR (runs verify, commits, pushes, opens PR)"
	@echo "  make meta        - Update repository metadata (description, topics)"
	@echo ""

bootstrap:
	@bash scripts/bootstrap.sh

verify:
	@echo "🔍 Running quality gates..."
	@if [ ! -f "repo.config.json" ]; then \
		echo "❌ repo.config.json not found"; \
		exit 1; \
	fi
	@echo ""
	@echo "📦 Installing dependencies..."
	@jq -r '.commands.install // empty' repo.config.json | bash || true
	@echo ""
	@echo "🔍 Running lint..."
	@jq -r '.commands.lint // empty' repo.config.json | bash || exit 1
	@echo ""
	@echo "🎨 Checking format..."
	@jq -r '.commands.format_check // empty' repo.config.json | bash || exit 1
	@echo ""
	@echo "🔬 Running typecheck..."
	@jq -r '.commands.typecheck // empty' repo.config.json | bash || exit 1
	@echo ""
	@echo "🧪 Running tests..."
	@jq -r '.commands.test // empty' repo.config.json | bash || exit 1
	@echo ""
	@echo "✅ All quality gates passed!"

pr:
	@bash scripts/pr.sh

meta:
	@bash scripts/repo_meta.sh

