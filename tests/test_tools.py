"""Tests for tools module."""

import pytest
from pytest_httpx import HTTPXMock

from langchain_ethys402.tools import (
    ConnectInput,
    DiscoverySearchInput,
    EthysConnectTool,
    EthysDiscoverySearchTool,
    EthysGetInfoTool,
    EthysTrustScoreTool,
    EthysVerifyPaymentTool,
    TelemetryInput,
    TrustScoreInput,
    VerifyPaymentInput,
)


def test_get_info_tool(httpx_mock: HTTPXMock) -> None:
    """Test EthysGetInfoTool."""
    httpx_mock.add_response(
        method="GET",
        url="https://402.ethys.dev/api/v1/402/info",
        json={
            "protocol": "x402",
            "name": "ETHYS",
            "description": "Test",
            "version": "1.0.0",
            "onboarding": {"steps": []},
            "pricing": {},
            "network": {},
            "endpoints": {},
            "features": [],
        },
    )
    result = EthysGetInfoTool.invoke({})
    assert result["success"] is True
    assert result["protocol"] == "x402"


def test_connect_tool(httpx_mock: HTTPXMock) -> None:
    """Test EthysConnectTool."""
    httpx_mock.add_response(
        method="POST",
        url="https://402.ethys.dev/api/v1/402/connect",
        json={"success": True, "agentId": "test_agent", "agentIdKey": "0x123"},
    )
    input_data = ConnectInput(
        address="0x1234567890123456789012345678901234567890",
        signature="0xabc",
        message="Test message",
    )
    result = EthysConnectTool.invoke(input_data.model_dump())
    assert result["success"] is True
    assert result["agent_id"] == "test_agent"


def test_verify_payment_tool(httpx_mock: HTTPXMock) -> None:
    """Test EthysVerifyPaymentTool."""
    httpx_mock.add_response(
        method="POST",
        url="https://402.ethys.dev/api/v1/402/verify-payment",
        json={"success": True, "agentId": "test_agent", "apiKey": "test_key"},
    )
    input_data = VerifyPaymentInput(agent_id="test_agent", tx_hash="0x123")
    result = EthysVerifyPaymentTool.invoke(input_data.model_dump())
    assert result["success"] is True
    assert result["api_key"] == "test_key"


def test_discovery_search_tool(httpx_mock: HTTPXMock) -> None:
    """Test EthysDiscoverySearchTool."""
    httpx_mock.add_response(
        method="GET",
        url="https://402.ethys.dev/api/v1/402/discovery/search",
        json={"success": True, "agents": [], "total": 0},
    )
    input_data = DiscoverySearchInput(query="test", min_trust_score=600)
    result = EthysDiscoverySearchTool.invoke(input_data.model_dump())
    assert result["success"] is True
    assert result["agents"] == []


def test_trust_score_tool(httpx_mock: HTTPXMock) -> None:
    """Test EthysTrustScoreTool."""
    httpx_mock.add_response(
        method="GET",
        url="https://402.ethys.dev/api/v1/402/trust/score",
        json={
            "success": True,
            "agentId": "test_agent",
            "trustScore": 750,
            "reliabilityScore": 0.85,
        },
    )
    input_data = TrustScoreInput(agent_id="test_agent")
    result = EthysTrustScoreTool.invoke(input_data.model_dump())
    assert result["success"] is True
    assert result["trust_score"] == 750


def test_trust_score_tool_missing_params() -> None:
    """Test EthysTrustScoreTool with missing parameters."""
    input_data = TrustScoreInput()
    with pytest.raises(Exception):  # Should raise ValidationError
        EthysTrustScoreTool.invoke(input_data.model_dump())

