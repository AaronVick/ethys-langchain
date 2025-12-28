## Summary

<!-- Brief description of changes in this PR -->

## Checklist

### Quality Gates
- [ ] Lint: `ruff check .` passes
- [ ] Format: `ruff format --check .` passes
- [ ] Typecheck: `mypy src` passes
- [ ] Tests: `pytest tests/ -v -m "not live"` passes

### Required Files
- [ ] `README.md` exists and is up to date
- [ ] `llms.txt` exists and is accurate
- [ ] `.well-known/agents.json` exists and is valid JSON
- [ ] `docs/12-28-review.md` exists (if applicable)

### Documentation
- [ ] README updated (if API changes)
- [ ] Examples updated (if behavior changes)
- [ ] Changelog updated (if user-facing changes)

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass (mocked)
- [ ] Live smoke tests pass (if applicable, opt-in)

## How to Test

```bash
# Run quality gates
make verify

# Run specific test suite
pytest tests/test_protocol_alignment.py -v

# Run live tests (opt-in)
ETHYS_LIVE_TESTS=1 pytest tests/ -m live
```

## Notes / Follow-ups

<!-- Any additional context, known issues, or follow-up tasks -->

