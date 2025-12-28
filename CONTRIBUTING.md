# Contributing to ETHYS LangChain

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ethys-langchain.git
   cd ethys-langchain
   ```
3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines

3. **Run quality gates** before committing:
   ```bash
   ruff check .
   ruff format .
   mypy src
   pytest tests/
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "Description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## Code Style

- **Linting**: We use `ruff` for linting (configured in `pyproject.toml`)
- **Formatting**: We use `ruff format` (configured in `pyproject.toml`)
- **Type Hints**: All functions must have type hints
- **Docstrings**: Google-style docstrings for all public APIs

### Running Quality Checks

```bash
# Linting
ruff check .

# Formatting (auto-fix)
ruff format .

# Type checking
mypy src

# Tests
pytest tests/ -v
```

## Testing

- **Write tests** for all new features
- **Update existing tests** if you change behavior
- **Ensure all tests pass** before submitting PR
- **Use mocks** for HTTP requests (no network required by default)

### Test Structure

- Unit tests: `tests/test_*.py`
- Integration tests: Use `httpx-mock` for HTTP mocking
- Live tests: Gated behind `ETHYS_LIVE_BASE_URL` env var

## Pull Request Guidelines

1. **Keep PRs focused** - one feature or fix per PR
2. **Write clear commit messages** - explain what and why
3. **Update documentation** if you add features or change APIs
4. **Add tests** for new functionality
5. **Ensure all quality gates pass** (CI will check)

### PR Checklist

- [ ] All quality gates pass (lint, format, type, test)
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commit messages are clear

## Documentation

- Update `README.md` if you add features
- Add docstrings to all public functions/classes
- Update examples if APIs change
- Keep protocol alignment documentation accurate

## Protocol Alignment

This package must align with ETHYS x402 protocol sources of truth:

- [Protocol Discovery](https://402.ethys.dev/.well-known/x402.json)
- [LLM Index](https://402.ethys.dev/llms.txt)
- [Live API Info](https://402.ethys.dev/api/v1/402/info)
- [Documentation](https://402.ethys.dev/)

If you find inconsistencies, document them explicitly (don't add silent fallbacks).

## Questions?

- Open an issue for questions or discussions
- Check existing issues/PRs for similar work
- Review the codebase to understand patterns

Thank you for contributing! 🎉

