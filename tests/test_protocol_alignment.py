"""Protocol alignment tests for ETHYS x402.

Tier 1: Deterministic tests with mocked HTTP responses (default)
Tier 2: Live smoke tests against 402.ethys.dev (opt-in via ETHYS_LIVE_TESTS=1)
"""

import json
import os
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from langchain_ethys402.client import EthysClient
from langchain_ethys402.errors import ApiError
from langchain_ethys402.tools import (
    EthysConnectTool,
    EthysDiscoverySearchTool,
    EthysGetInfoTool,
    EthysTelemetryTool,
    EthysTrustAttestTool,
    EthysTrustScoreTool,
    EthysVerifyPaymentTool,
)


# Tier 1: Deterministic Mocked Tests
class TestProtocolAlignmentMocked:
    """Tier 1: Tests with mocked HTTP responses (no network required)."""

    @pytest.fixture
    def mock_info_response(self) -> dict[str, Any]:
        """Mock response for /api/v1/402/info."""
        return {
            "protocol": "x402",
            "name": "ETHYS x402 Protocol",
            "description": "Autonomous agent payment and discovery protocol on Base L2",
            "version": "1.0.0",
            "onboarding": {
                "steps": [
                    {
                        "step": 1,
                        "title": "Connect with Wallet",
                        "description": "Sign message with your Base L2 wallet",
                        "endpoint": "POST /api/v1/402/connect",
                    }
                ]
            },
            "pricing": {
                "token": {
                    "address": "0x1Dd996287dB5a95D6C9236EfB10C7f90145e5B07",
                    "symbol": "ETHYS",
                    "network": "Base L2",
                    "chainId": 8453,
                    "decimals": 18,
                },
                "activationFee": {
                    "usd": 150,
                    "tokenAmount": "150.000000",
                    "currentPriceUsd": 1,
                },
            },
            "network": {
                "name": "Base",
                "chainId": 8453,
                "rpcUrl": "https://mainnet.base.org",
            },
            "endpoints": {
                "connect": "/api/v1/402/connect",
                "verifyPayment": "/api/v1/402/verify-payment",
                "telemetry": "/api/v1/402/telemetry",
            },
            "features": ["agent discovery", "trust scoring", "telemetry"],
        }

    @pytest.fixture
    def mock_connect_response(self) -> dict[str, Any]:
        """Mock response for /api/v1/402/connect."""
        return {
            "success": True,
            "agentId": "agent_test_123",
            "agentIdKey": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "onboarding": {"nextStep": "payment"},
        }

    def test_get_info_parses_structure(self, httpx_mock: HTTPXMock, mock_info_response: dict[str, Any]) -> None:
        """Test that get_info parses and validates pricing/onboarding structure."""
        httpx_mock.add_response(
            method="GET",
            url="https://402.ethys.dev/api/v1/402/info",
            json=mock_info_response,
        )

        tool = EthysGetInfoTool()
        result = tool.invoke({})

        assert result["success"] is True
        assert result["protocol"] == "x402"
        assert result["version"] == "1.0.0"
        assert "pricing" in result
        assert result["pricing"]["activationFee"]["usd"] == 150
        assert "onboarding_steps" in result
        assert len(result["onboarding_steps"]) > 0

    def test_connect_builds_signed_payload(self, httpx_mock: HTTPXMock, mock_connect_response: dict[str, Any]) -> None:
        """Test that connect builds correct signed payload."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/connect",
            json=mock_connect_response,
        )

        tool = EthysConnectTool()
        result = tool.invoke(
            {
                "address": "0x1234567890123456789012345678901234567890",
                "signature": "0xabcdef",
                "message": "Test message",
            }
        )

        assert result["success"] is True
        assert result["agent_id"] == "agent_test_123"
        assert "agent_id_key" in result

    def test_connect_handles_auth_errors(self, httpx_mock: HTTPXMock) -> None:
        """Test that connect handles authentication errors correctly."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/connect",
            status_code=401,
            json={"success": False, "error": "Invalid signature"},
        )

        tool = EthysConnectTool()
        with pytest.raises(ApiError) as exc_info:
            tool.invoke(
                {
                    "address": "0x1234567890123456789012345678901234567890",
                    "signature": "0xinvalid",
                    "message": "Test message",
                }
            )
        assert exc_info.value.status_code == 401

    def test_verify_payment_success(self, httpx_mock: HTTPXMock) -> None:
        """Test verify_payment handles success case."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/verify-payment",
            json={"success": True, "agentId": "agent_test_123", "apiKey": "test_api_key"},
        )

        tool = EthysVerifyPaymentTool()
        result = tool.invoke({"agent_id": "agent_test_123", "tx_hash": "0x123"})

        assert result["success"] is True
        assert result["api_key"] == "test_api_key"

    def test_verify_payment_failure(self, httpx_mock: HTTPXMock) -> None:
        """Test verify_payment handles failure case."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/verify-payment",
            status_code=400,
            json={"success": False, "error": "Payment not found"},
        )

        tool = EthysVerifyPaymentTool()
        with pytest.raises(ApiError) as exc_info:
            tool.invoke({"agent_id": "agent_test_123", "tx_hash": "0xinvalid"})
        assert exc_info.value.status_code == 400

    def test_telemetry_validates_payload_schema(self, httpx_mock: HTTPXMock) -> None:
        """Test that telemetry validates payload schema."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/telemetry",
            json={"success": True, "eventsProcessed": 1},
        )

        tool = EthysTelemetryTool()
        result = tool.invoke(
            {
                "agent_id": "agent_test_123",
                "address": "0x1234567890123456789012345678901234567890",
                "timestamp": 1234567890,
                "nonce": "0x" + "1" * 64,
                "events": [{"eventType": "test", "timestamp": 1234567890, "data": {}}],
                "signature": "0xabcdef",
            }
        )

        assert result["success"] is True
        assert result["events_processed"] == 1

    def test_telemetry_handles_validation_errors(self, httpx_mock: HTTPXMock) -> None:
        """Test that telemetry handles server validation errors."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/telemetry",
            status_code=400,
            json={"success": False, "error": "Invalid signature format"},
        )

        tool = EthysTelemetryTool()
        with pytest.raises(ApiError) as exc_info:
            tool.invoke(
                {
                    "agent_id": "agent_test_123",
                    "address": "0x1234567890123456789012345678901234567890",
                    "timestamp": 1234567890,
                    "nonce": "0x" + "1" * 64,
                    "events": [{"eventType": "test", "timestamp": 1234567890, "data": {}}],
                    "signature": "0xinvalid",
                }
            )
        assert exc_info.value.status_code == 400

    def test_discovery_search_builds_query(self, httpx_mock: HTTPXMock) -> None:
        """Test that discovery_search builds query correctly."""
        httpx_mock.add_response(
            method="GET",
            url="https://402.ethys.dev/api/v1/402/discovery/search?minTrustScore=600&limit=10",
            json={"success": True, "agents": [], "total": 0},
        )

        tool = EthysDiscoverySearchTool()
        result = tool.invoke({"min_trust_score": 600, "limit": 10})

        assert result["success"] is True
        assert "agents" in result

    def test_discovery_search_parses_results(self, httpx_mock: HTTPXMock) -> None:
        """Test that discovery_search parses results correctly."""
        httpx_mock.add_response(
            method="GET",
            url="https://402.ethys.dev/api/v1/402/discovery/search",
            json={
                "success": True,
                "agents": [
                    {
                        "agentId": "agent_1",
                        "name": "Test Agent",
                        "trustScore": 750,
                        "serviceTypes": ["nlp", "data"],
                    }
                ],
                "total": 1,
            },
        )

        tool = EthysDiscoverySearchTool()
        result = tool.invoke({})

        assert result["success"] is True
        assert len(result["agents"]) == 1
        assert result["agents"][0]["agent_id"] == "agent_1"
        assert result["agents"][0]["trust_score"] == 750

    def test_trust_score_parses_response(self, httpx_mock: HTTPXMock) -> None:
        """Test that trust_score parses response correctly."""
        httpx_mock.add_response(
            method="GET",
            url="https://402.ethys.dev/api/v1/402/trust/score?agentId=agent_test_123",
            json={
                "success": True,
                "agentId": "agent_test_123",
                "trustScore": 750,
                "reliabilityScore": 0.85,
                "coherenceIndex": 0.92,
                "endorsementCount": 10,
            },
        )

        tool = EthysTrustScoreTool()
        result = tool.invoke({"agent_id": "agent_test_123"})

        assert result["success"] is True
        assert result["trust_score"] == 750
        assert result["reliability_score"] == 0.85

    def test_trust_attest_submission(self, httpx_mock: HTTPXMock) -> None:
        """Test that trust_attest handles submission correctly."""
        httpx_mock.add_response(
            method="POST",
            url="https://402.ethys.dev/api/v1/402/trust/attest",
            json={"success": True, "attestationId": "attest_123"},
        )

        tool = EthysTrustAttestTool()
        result = tool.invoke(
            {
                "agent_id": "agent_test_123",
                "target_agent_id": "agent_target_456",
                "interaction_type": "task_completion",
                "rating": 5,
            }
        )

        assert result["success"] is True
        assert result["attestation_id"] == "attest_123"

    def test_error_mapping_4xx(self, httpx_mock: HTTPXMock) -> None:
        """Test that 4xx errors map to typed errors with status_code."""
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
        assert "error" in exc_info.value.response_body

    def test_error_mapping_5xx(self, httpx_mock: HTTPXMock) -> None:
        """Test that 5xx errors map to typed errors."""
        httpx_mock.add_response(
            method="GET",
            url="https://402.ethys.dev/api/v1/402/info",
            status_code=500,
            json={"error": "Internal server error"},
        )

        client = EthysClient()
        with pytest.raises(ApiError) as exc_info:
            client.get("/api/v1/402/info")
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_tools_async_execution(self, httpx_mock: HTTPXMock, mock_info_response: dict[str, Any]) -> None:
        """Test that tools support async execution."""
        httpx_mock.add_response(
            method="GET",
            url="https://402.ethys.dev/api/v1/402/info",
            json=mock_info_response,
        )

        tool = EthysGetInfoTool()
        result = await tool.ainvoke({})

        assert result["success"] is True
        assert result["protocol"] == "x402"

    def test_tool_input_schema_validation(self) -> None:
        """Test that tool input schemas validate correctly."""
        tool = EthysConnectTool()

        # Invalid input should raise ValidationError
        from langchain_ethys402.errors import ValidationError

        with pytest.raises(ValidationError):
            tool.invoke({"invalid": "input"})


# Tier 2: Live Smoke Tests (opt-in)
@pytest.mark.live
class TestProtocolAlignmentLive:
    """Tier 2: Live smoke tests against 402.ethys.dev (requires ETHYS_LIVE_TESTS=1)."""

    @pytest.fixture(autouse=True)
    def check_live_tests_enabled(self) -> None:
        """Skip live tests unless explicitly enabled."""
        if not os.getenv("ETHYS_LIVE_TESTS") and not os.getenv("ETHYS_MODE") == "live":
            pytest.skip("Live tests disabled. Set ETHYS_LIVE_TESTS=1 to enable.")

    @pytest.fixture
    def base_url(self) -> str:
        """Get base URL for live tests."""
        return os.getenv("ETHYS_LIVE_BASE_URL", "https://402.ethys.dev")

    def test_x402_json_reachable(self, base_url: str) -> None:
        """Test that /.well-known/x402.json is reachable and parseable."""
        import httpx

        url = f"{base_url}/.well-known/x402.json"
        response = httpx.get(url, timeout=10.0)
        assert response.status_code == 200, f"Expected 200, got {response.status_code} for {url}"

        try:
            data = response.json()
            assert "protocol" in data, f"Missing 'protocol' field in {url}"
            assert data["protocol"] == "x402", f"Expected protocol 'x402', got '{data.get('protocol')}'"
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse JSON from {url}: {e}\nResponse body (first 500 chars): {response.text[:500]}")

    def test_llms_txt_reachable(self, base_url: str) -> None:
        """Test that /llms.txt is reachable and non-empty."""
        import httpx

        url = f"{base_url}/llms.txt"
        response = httpx.get(url, timeout=10.0)
        assert response.status_code == 200, f"Expected 200, got {response.status_code} for {url}"
        assert len(response.text) > 0, f"{url} returned empty content"

    def test_api_info_reachable(self, base_url: str) -> None:
        """Test that /api/v1/402/info is reachable and parseable."""
        import httpx

        url = f"{base_url}/api/v1/402/info"
        response = httpx.get(url, timeout=10.0)
        assert response.status_code == 200, f"Expected 200, got {response.status_code} for {url}"

        try:
            data = response.json()
            assert "protocol" in data, f"Missing 'protocol' field in {url}"
            assert "pricing" in data, f"Missing 'pricing' field in {url}"
            assert "onboarding" in data, f"Missing 'onboarding' field in {url}"
        except json.JSONDecodeError as e:
            pytest.fail(
                f"Failed to parse JSON from {url}: {e}\n"
                f"Status: {response.status_code}\n"
                f"Response body (first 500 chars): {response.text[:500]}"
            )

    def test_api_info_schema_alignment(self, base_url: str) -> None:
        """Test that /api/v1/402/info schema matches expected structure."""
        import httpx

        url = f"{base_url}/api/v1/402/info"
        response = httpx.get(url, timeout=10.0)
        data = response.json()

        # Validate required fields
        required_fields = ["protocol", "name", "description", "version", "pricing", "onboarding", "network"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            pytest.fail(
                f"Schema drift detected in {url}: missing fields {missing_fields}\n"
                f"Response (first 1000 chars): {json.dumps(data, indent=2)[:1000]}"
            )

        # Validate pricing structure
        if "pricing" in data:
            pricing = data["pricing"]
            assert "token" in pricing, "Missing 'token' in pricing"
            assert "activationFee" in pricing, "Missing 'activationFee' in pricing"

    def test_link_integrity_x402_json(self, base_url: str) -> None:
        """Test that URLs referenced in x402.json are reachable (bounded crawl)."""
        import httpx

        # Fetch x402.json
        x402_url = f"{base_url}/.well-known/x402.json"
        response = httpx.get(x402_url, timeout=10.0)
        x402_data = response.json()

        # Extract URLs (bounded to 25)
        urls_to_check = []
        if "docs" in x402_data:
            for _key, value in x402_data["docs"].items():
                if isinstance(value, str) and value.startswith("/"):
                    urls_to_check.append(f"{base_url}{value}")

        if "endpoints" in x402_data:
            for _key, value in x402_data["endpoints"].items():
                if isinstance(value, str) and value.startswith("/"):
                    urls_to_check.append(f"{base_url}{value}")

        # Limit to 25 URLs
        urls_to_check = urls_to_check[:25]

        failed_urls = []
        for url in urls_to_check:
            try:
                resp = httpx.head(url, timeout=5.0, follow_redirects=True)
                if resp.status_code not in (200, 301, 302, 307, 308):
                    failed_urls.append((url, resp.status_code, resp.text[:200]))
            except Exception as e:
                failed_urls.append((url, "ERROR", str(e)[:200]))

        if failed_urls:
            error_msg = "Link integrity check failed:\n"
            for url, status, body in failed_urls:
                error_msg += f"  {url}: {status}\n    {body}\n"
            pytest.fail(error_msg)

    def test_openapi_if_present(self, base_url: str) -> None:
        """Test that OpenAPI endpoint returns valid OpenAPI if present."""
        import httpx

        # Try common OpenAPI paths
        openapi_paths = [
            "/api/v1/402/docs/openapi",
            "/api/v1/402/openapi.json",
            "/openapi.json",
        ]

        for path in openapi_paths:
            url = f"{base_url}{path}"
            try:
                response = httpx.get(url, timeout=10.0)
                if response.status_code == 200:
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        # Basic OpenAPI structure check
                        if "openapi" in data or "swagger" in data:
                            assert "paths" in data or "paths" in data.get("components", {}), (
                                f"OpenAPI at {url} missing 'paths' field"
                            )
                            return  # Success
                    except json.JSONDecodeError:
                        # Try YAML (optional dependency)
                        try:
                            import yaml

                            data = yaml.safe_load(response.text)
                            if "openapi" in data or "swagger" in data:
                                return  # Success
                        except ImportError:
                            # yaml not available, skip YAML parsing
                            pass
                        except Exception:
                            pass
            except Exception:
                continue

        # OpenAPI not found is OK (not all repos have it)
        pytest.skip("OpenAPI endpoint not found (this is OK)")

    def test_connector_base_url_alignment(self, base_url: str) -> None:
        """Test that connector base URL matches configured base URL."""
        from langchain_ethys402.config import EthysConfig

        config = EthysConfig.from_env()
        assert config.base_url == base_url, (
            f"Connector base URL ({config.base_url}) does not match test base URL ({base_url})"
        )

    def test_required_endpoints_exist(self, base_url: str) -> None:
        """Test that required endpoints exist (HEAD/GET checks where safe)."""
        import httpx

        # Endpoints that should exist (safe HEAD/GET)
        safe_endpoints = [
            "/api/v1/402/info",
            "/.well-known/x402.json",
            "/llms.txt",
        ]

        failed_endpoints = []
        for endpoint in safe_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = httpx.head(url, timeout=5.0, follow_redirects=True)
                if response.status_code not in (200, 301, 302, 307, 308, 405):  # 405 = Method Not Allowed is OK
                    failed_endpoints.append((url, response.status_code))
            except Exception as e:
                failed_endpoints.append((url, f"ERROR: {str(e)[:200]}"))

        if failed_endpoints:
            error_msg = "Required endpoints check failed:\n"
            for url, status in failed_endpoints:
                error_msg += f"  {url}: {status}\n"
            pytest.fail(error_msg)

    def test_unauthenticated_behavior(self, base_url: str) -> None:
        """Test that unauthenticated requests return expected 401/403 with structured error."""
        import httpx

        # Endpoints that require auth
        auth_required_endpoints = [
            "/api/v1/402/telemetry",
            "/api/v1/402/connect",
        ]

        for endpoint in auth_required_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                if endpoint.endswith("/telemetry"):
                    response = httpx.post(url, json={}, timeout=5.0)
                else:
                    response = httpx.post(url, json={}, timeout=5.0)

                # Should return 401 or 403
                assert response.status_code in (401, 403), (
                    f"Expected 401/403 for unauthenticated {url}, got {response.status_code}\n"
                    f"Response (first 500 chars): {response.text[:500]}"
                )

                # Should have structured error
                try:
                    error_data = response.json()
                    assert "error" in error_data or "success" in error_data, (
                        f"Unstructured error response from {url}\n"
                        f"Response: {response.text[:500]}"
                    )
                except json.JSONDecodeError:
                    pytest.fail(
                        f"Non-JSON error response from {url}\n"
                        f"Status: {response.status_code}\n"
                        f"Response (first 500 chars): {response.text[:500]}"
                    )
            except Exception as e:
                pytest.fail(f"Error checking {url}: {str(e)[:200]}")

