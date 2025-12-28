"""Pytest configuration and fixtures for protocol alignment tests."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "live: marks tests as live (require ETHYS_LIVE_TESTS=1)")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip live tests unless explicitly enabled."""
    if not config.getoption("--live", default=False):
        skip_live = pytest.mark.skip(reason="Live tests disabled. Use --live flag or ETHYS_LIVE_TESTS=1")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command-line options."""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live tests against 402.ethys.dev (requires ETHYS_LIVE_TESTS=1)",
    )

