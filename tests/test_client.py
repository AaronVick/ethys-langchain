"""Tests for client module."""

import pytest
from httpx import Response
from pytest_httpx import HTTPXMock

from langchain_ethys402.client import EthysClient
from langchain_ethys402.config import EthysConfig
from langchain_ethys402.errors import ApiError, NetworkError, TimeoutError


def test_client_init_default() -> None:
    """Test client initialization with defaults."""
    client = EthysClient()
    assert client.config.base_url == "https://402.ethys.dev"
    assert client.config.timeout == 30.0


def test_client_init_custom() -> None:
    """Test client initialization with custom config."""
    config = EthysConfig(base_url="https://test.example.com", timeout=60.0)
    client = EthysClient(config=config)
    assert client.config.base_url == "https://test.example.com"
    assert client.config.timeout == 60.0


def test_client_get_success(httpx_mock: HTTPXMock) -> None:
    """Test successful GET request."""
    httpx_mock.add_response(
        method="GET",
        url="https://402.ethys.dev/api/v1/402/info",
        json={"protocol": "x402", "version": "1.0.0"},
    )
    client = EthysClient()
    response = client.get("/api/v1/402/info")
    assert response["protocol"] == "x402"
    assert response["version"] == "1.0.0"


def test_client_get_api_error(httpx_mock: HTTPXMock) -> None:
    """Test GET request with API error."""
    httpx_mock.add_response(
        method="GET",
        url="https://402.ethys.dev/api/v1/402/info",
        status_code=404,
        json={"error": "Not found"},
    )
    client = EthysClient()
    with pytest.raises(ApiError) as exc_info:
        client.get("/api/v1/402/info")
    assert exc_info.value.status_code == 404


def test_client_post_success(httpx_mock: HTTPXMock) -> None:
    """Test successful POST request."""
    httpx_mock.add_response(
        method="POST",
        url="https://402.ethys.dev/api/v1/402/connect",
        json={"success": True, "agentId": "test_agent"},
    )
    client = EthysClient()
    response = client.post("/api/v1/402/connect", data={"address": "0x123"})
    assert response["success"] is True
    assert response["agentId"] == "test_agent"


@pytest.mark.asyncio
async def test_client_aget_success(httpx_mock: HTTPXMock) -> None:
    """Test successful async GET request."""
    httpx_mock.add_response(
        method="GET",
        url="https://402.ethys.dev/api/v1/402/info",
        json={"protocol": "x402", "version": "1.0.0"},
    )
    client = EthysClient()
    response = await client.aget("/api/v1/402/info")
    assert response["protocol"] == "x402"
    assert response["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_client_apost_success(httpx_mock: HTTPXMock) -> None:
    """Test successful async POST request."""
    httpx_mock.add_response(
        method="POST",
        url="https://402.ethys.dev/api/v1/402/connect",
        json={"success": True, "agentId": "test_agent"},
    )
    client = EthysClient()
    response = await client.apost("/api/v1/402/connect", data={"address": "0x123"})
    assert response["success"] is True
    assert response["agentId"] == "test_agent"

