# Release PR Workflow

This repository includes a fully programmatic Release PR workflow using GitHub CLI.

## Quick Start

```bash
# 1. Verify prerequisites
make bootstrap

# 2. Run quality gates
make verify

# 3. Create release PR
make pr
```

## Prerequisites

- `git` - Version control
- `gh` - GitHub CLI (https://cli.github.com/)
- `jq` - JSON processor (https://stedolan.github.io/jq/)
- GitHub CLI authenticated: `gh auth login`

## Workflow Details

### `make bootstrap`
Verifies all prerequisites are installed and configured:
- ✅ git installed
- ✅ GitHub CLI installed and authenticated
- ✅ jq installed
- ✅ In a git repository
- ✅ repo.config.json exists

### `make verify`
Runs all quality gates:
- Install dependencies
- Lint (`ruff check .`)
- Format check (`ruff format --check .`)
- Typecheck (`mypy src`)
- Tests (`pytest tests/ -v -m "not live"`)

**Fails fast** - stops on first error with clear message.

### `make pr`
Complete release PR workflow:
1. Creates branch: `chore/release-pr-YYYY-MM-DD`
2. Verifies required files exist
3. Runs all quality gates (same as `make verify`)
4. Commits changes (if any)
5. Pushes branch
6. Opens PR with:
   - Title: "Release readiness: ethys-langchain (YYYY-MM-DD)"
   - Body: Generated with checklist and summary
   - Labels: release, automation, docs, tests
   - Reviewers: (from config)

**No PR created if gates fail.**

### `make meta`
Updates repository metadata:
- Sets description based on repo type
- Sets GitHub topics (ethys, x402, langchain, etc.)

Requires repository write permissions.

## Configuration

Edit `repo.config.json` to customize:
- Repository name and type
- Default branch
- Reviewers
- Labels
- Quality gate commands
- Required files

## PR Template

All PRs use `.github/pull_request_template.md` with:
- Summary section
- Quality gates checklist
- Required files checklist
- Testing instructions

## CI Alignment

CI runs the same gates as `make verify`:
- PR/push: lint, format, typecheck, tests (Tier 1)
- Scheduled: live smoke tests (Tier 2, opt-in)

See `.github/workflows/ci.yml` for details.
