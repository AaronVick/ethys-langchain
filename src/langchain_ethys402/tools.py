"""LangChain Tools for ETHYS x402 API."""

from typing import Any, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from langchain_ethys402.client import EthysClient
from langchain_ethys402.errors import ValidationError
from langchain_ethys402.types import (
    ConnectRequest,
    ConnectResponse,
    DiscoverySearchParams,
    DiscoverySearchResponse,
    InfoResponse,
    ReviewsSubmitRequest,
    ReviewsSubmitResponse,
    TelemetryEvent,
    TelemetryRequest,
    TelemetryResponse,
    TrustAttestRequest,
    TrustAttestResponse,
    TrustScoreRequest,
    TrustScoreResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)


# Input schemas for tools
class ConnectInput(BaseModel):
    """Input schema for EthysConnectTool."""

    address: str = Field(..., description="Ethereum wallet address (0x-prefixed)")
    signature: str = Field(..., description="Wallet signature of the message")
    message: str = Field(..., description="Message that was signed")


class VerifyPaymentInput(BaseModel):
    """Input schema for EthysVerifyPaymentTool."""

    agent_id: str = Field(..., description="Agent ID from connect step")
    tx_hash: Optional[str] = Field(None, description="Transaction hash (optional, auto-detected if not provided)")


class TelemetryInput(BaseModel):
    """Input schema for EthysTelemetryTool."""

    agent_id: str = Field(..., description="Agent ID")
    address: str = Field(..., description="Wallet address")
    timestamp: int = Field(..., description="Unix timestamp")
    nonce: str = Field(..., description="32-byte hex nonce")
    events: list[dict[str, Any]] = Field(..., description="List of telemetry events")
    signature: str = Field(..., description="Wallet signature of the telemetry payload")


class DiscoverySearchInput(BaseModel):
    """Input schema for EthysDiscoverySearchTool."""

    query: Optional[str] = Field(None, description="Search query string")
    min_trust_score: Optional[int] = Field(None, description="Minimum trust score")
    service_types: Optional[str] = Field(None, description="Comma-separated service types")
    limit: Optional[int] = Field(None, description="Maximum number of results")
    offset: Optional[int] = Field(None, description="Pagination offset")


class TrustScoreInput(BaseModel):
    """Input schema for EthysTrustScoreTool."""

    agent_id: Optional[str] = Field(None, description="Agent ID")
    agent_id_key: Optional[str] = Field(None, description="Agent ID key (bytes32 hex)")


class TrustAttestInput(BaseModel):
    """Input schema for EthysTrustAttestTool."""

    agent_id: str = Field(..., description="Your agent ID")
    target_agent_id: str = Field(..., description="Target agent ID")
    interaction_type: str = Field(..., description="Type of interaction")
    rating: Optional[int] = Field(None, description="Rating (1-5)")
    notes: Optional[str] = Field(None, description="Optional notes")


class ReviewsSubmitInput(BaseModel):
    """Input schema for EthysReviewsSubmitTool."""

    agent_id: str = Field(..., description="Agent ID being reviewed")
    rating: int = Field(..., description="Rating (1-5)")
    signature: str = Field(..., description="EIP-712 signature")
    review_text: Optional[str] = Field(None, description="Review text")
    domain: Optional[dict[str, Any]] = Field(None, description="EIP-712 domain")
    types: Optional[dict[str, Any]] = Field(None, description="EIP-712 types")
    message: Optional[dict[str, Any]] = Field(None, description="EIP-712 message")


def _get_info_sync() -> dict[str, Any]:
    """Get ETHYS protocol info (sync)."""
    client = EthysClient()
    response = client.get("/api/v1/402/info")
    info = InfoResponse(**response)
    return {
        "success": True,
        "protocol": info.protocol,
        "version": info.version,
        "description": info.description,
        "pricing": info.pricing,
        "onboarding_steps": info.onboarding.get("steps", []),
        "network": info.network,
        "endpoints": info.endpoints,
        "features": info.features,
    }


async def _get_info_async() -> dict[str, Any]:
    """Get ETHYS protocol info (async)."""
    client = EthysClient()
    response = await client.aget("/api/v1/402/info")
    info = InfoResponse(**response)
    return {
        "success": True,
        "protocol": info.protocol,
        "version": info.version,
        "description": info.description,
        "pricing": info.pricing,
        "onboarding_steps": info.onboarding.get("steps", []),
        "network": info.network,
        "endpoints": info.endpoints,
        "features": info.features,
    }


EthysGetInfoTool = StructuredTool.from_function(
    func=_get_info_sync,
    coroutine=_get_info_async,
    name="ethys_get_info",
    description=(
        "Get ETHYS x402 protocol information including pricing, onboarding steps, "
        "network configuration, and available endpoints. No authentication required."
    ),
)


def _connect_sync(input_data: ConnectInput) -> dict[str, Any]:
    """Connect agent (sync)."""
    client = EthysClient()
    request = ConnectRequest(
        address=input_data.address, signature=input_data.signature, message=input_data.message
    )
    response = client.post("/api/v1/402/connect", data=request.model_dump(by_alias=True))
    connect_response = ConnectResponse(**response)
    return {
        "success": connect_response.success,
        "agent_id": connect_response.agent_id,
        "agent_id_key": connect_response.agent_id_key,
        "onboarding": connect_response.onboarding,
    }


async def _connect_async(input_data: ConnectInput) -> dict[str, Any]:
    """Connect agent (async)."""
    client = EthysClient()
    request = ConnectRequest(
        address=input_data.address, signature=input_data.signature, message=input_data.message
    )
    response = await client.apost("/api/v1/402/connect", data=request.model_dump(by_alias=True))
    connect_response = ConnectResponse(**response)
    return {
        "success": connect_response.success,
        "agent_id": connect_response.agent_id,
        "agent_id_key": connect_response.agent_id_key,
        "onboarding": connect_response.onboarding,
    }


EthysConnectTool = StructuredTool.from_function(
    func=_connect_sync,
    coroutine=_connect_async,
    name="ethys_connect",
    description=(
        "Connect/register an agent with ETHYS using wallet signature. "
        "Requires: address (wallet address), signature (wallet signature), "
        "and message (the message that was signed). "
        "Returns agent_id and onboarding information."
    ),
    args_schema=ConnectInput,
)


def _verify_payment_sync(input_data: VerifyPaymentInput) -> dict[str, Any]:
    """Verify payment (sync)."""
    client = EthysClient()
    request = VerifyPaymentRequest(agent_id=input_data.agent_id, tx_hash=input_data.tx_hash)
    response = client.post("/api/v1/402/verify-payment", data=request.model_dump(by_alias=True))
    verify_response = VerifyPaymentResponse(**response)
    return {
        "success": verify_response.success,
        "message": verify_response.message,
        "agent_id": verify_response.agent_id,
        "api_key": verify_response.api_key,
    }


async def _verify_payment_async(input_data: VerifyPaymentInput) -> dict[str, Any]:
    """Verify payment (async)."""
    client = EthysClient()
    request = VerifyPaymentRequest(agent_id=input_data.agent_id, tx_hash=input_data.tx_hash)
    response = await client.apost("/api/v1/402/verify-payment", data=request.model_dump(by_alias=True))
    verify_response = VerifyPaymentResponse(**response)
    return {
        "success": verify_response.success,
        "message": verify_response.message,
        "agent_id": verify_response.agent_id,
        "api_key": verify_response.api_key,
    }


EthysVerifyPaymentTool = StructuredTool.from_function(
    func=_verify_payment_sync,
    coroutine=_verify_payment_async,
    name="ethys_verify_payment",
    description=(
        "Verify ETHYS payment transaction after calling buyTierAuto() on the purchase contract. "
        "Requires: agent_id (from connect) and optionally tx_hash (transaction hash). "
        "Returns success status and API key if payment is verified."
    ),
    args_schema=VerifyPaymentInput,
)


def _telemetry_sync(input_data: TelemetryInput) -> dict[str, Any]:
    """Submit telemetry (sync)."""
    client = EthysClient()
    # Validate events
    telemetry_events = [TelemetryEvent(**event) for event in input_data.events]
    request = TelemetryRequest(
        agent_id=input_data.agent_id,
        address=input_data.address,
        ts=input_data.timestamp,
        nonce=input_data.nonce,
        events=[e.model_dump(by_alias=True) for e in telemetry_events],
        signature=input_data.signature,
    )
    response = client.post("/api/v1/402/telemetry", data=request.model_dump(by_alias=True))
    telemetry_response = TelemetryResponse(**response)
    return {
        "success": telemetry_response.success,
        "message": telemetry_response.message,
        "events_processed": telemetry_response.events_processed,
    }


async def _telemetry_async(input_data: TelemetryInput) -> dict[str, Any]:
    """Submit telemetry (async)."""
    client = EthysClient()
    # Validate events
    telemetry_events = [TelemetryEvent(**event) for event in input_data.events]
    request = TelemetryRequest(
        agent_id=input_data.agent_id,
        address=input_data.address,
        ts=input_data.timestamp,
        nonce=input_data.nonce,
        events=[e.model_dump(by_alias=True) for e in telemetry_events],
        signature=input_data.signature,
    )
    response = await client.apost("/api/v1/402/telemetry", data=request.model_dump(by_alias=True))
    telemetry_response = TelemetryResponse(**response)
    return {
        "success": telemetry_response.success,
        "message": telemetry_response.message,
        "events_processed": telemetry_response.events_processed,
    }


EthysTelemetryTool = StructuredTool.from_function(
    func=_telemetry_sync,
    coroutine=_telemetry_async,
    name="ethys_telemetry",
    description=(
        "Submit agent telemetry events with wallet signature. "
        "Requires: agent_id, address, timestamp, nonce, events (list of event dicts), "
        "and signature (wallet signature of the payload). "
        "Returns success status and number of events processed."
    ),
    args_schema=TelemetryInput,
)


def _discovery_search_sync(input_data: DiscoverySearchInput) -> dict[str, Any]:
    """Search discovery (sync)."""
    client = EthysClient()
    params = DiscoverySearchParams(
        query=input_data.query,
        min_trust_score=input_data.min_trust_score,
        service_types=input_data.service_types,
        limit=input_data.limit,
        offset=input_data.offset,
    )
    query_params = params.model_dump(by_alias=True, exclude_none=True)
    response = client.get("/api/v1/402/discovery/search", params=query_params)
    search_response = DiscoverySearchResponse(**response)
    return {
        "success": search_response.success,
        "agents": [agent.model_dump(by_alias=True) for agent in search_response.agents],
        "total": search_response.total,
        "limit": search_response.limit,
        "offset": search_response.offset,
    }


async def _discovery_search_async(input_data: DiscoverySearchInput) -> dict[str, Any]:
    """Search discovery (async)."""
    client = EthysClient()
    params = DiscoverySearchParams(
        query=input_data.query,
        min_trust_score=input_data.min_trust_score,
        service_types=input_data.service_types,
        limit=input_data.limit,
        offset=input_data.offset,
    )
    query_params = params.model_dump(by_alias=True, exclude_none=True)
    response = await client.aget("/api/v1/402/discovery/search", params=query_params)
    search_response = DiscoverySearchResponse(**response)
    return {
        "success": search_response.success,
        "agents": [agent.model_dump(by_alias=True) for agent in search_response.agents],
        "total": search_response.total,
        "limit": search_response.limit,
        "offset": search_response.offset,
    }


EthysDiscoverySearchTool = StructuredTool.from_function(
    func=_discovery_search_sync,
    coroutine=_discovery_search_async,
    name="ethys_discovery_search",
    description=(
        "Search for agents in the ETHYS discovery system. "
        "Optional parameters: query (search string), min_trust_score (minimum trust score), "
        "service_types (comma-separated list), limit (max results), offset (pagination). "
        "Returns list of matching agents with their trust scores and capabilities."
    ),
    args_schema=DiscoverySearchInput,
)


def _trust_score_sync(input_data: TrustScoreInput) -> dict[str, Any]:
    """Get trust score (sync)."""
    if not input_data.agent_id and not input_data.agent_id_key:
        raise ValidationError("Either agent_id or agent_id_key must be provided")
    client = EthysClient()
    params = TrustScoreRequest(agent_id=input_data.agent_id, agent_id_key=input_data.agent_id_key)
    query_params = params.model_dump(by_alias=True, exclude_none=True)
    response = client.get("/api/v1/402/trust/score", params=query_params)
    trust_response = TrustScoreResponse(**response)
    return {
        "success": trust_response.success,
        "agent_id": trust_response.agent_id,
        "agent_id_key": trust_response.agent_id_key,
        "trust_score": trust_response.trust_score,
        "reliability_score": trust_response.reliability_score,
        "coherence_index": trust_response.coherence_index,
        "endorsement_count": trust_response.endorsement_count,
    }


async def _trust_score_async(input_data: TrustScoreInput) -> dict[str, Any]:
    """Get trust score (async)."""
    if not input_data.agent_id and not input_data.agent_id_key:
        raise ValidationError("Either agent_id or agent_id_key must be provided")
    client = EthysClient()
    params = TrustScoreRequest(agent_id=input_data.agent_id, agent_id_key=input_data.agent_id_key)
    query_params = params.model_dump(by_alias=True, exclude_none=True)
    response = await client.aget("/api/v1/402/trust/score", params=query_params)
    trust_response = TrustScoreResponse(**response)
    return {
        "success": trust_response.success,
        "agent_id": trust_response.agent_id,
        "agent_id_key": trust_response.agent_id_key,
        "trust_score": trust_response.trust_score,
        "reliability_score": trust_response.reliability_score,
        "coherence_index": trust_response.coherence_index,
        "endorsement_count": trust_response.endorsement_count,
    }


EthysTrustScoreTool = StructuredTool.from_function(
    func=_trust_score_sync,
    coroutine=_trust_score_async,
    name="ethys_trust_score",
    description=(
        "Get agent trust score and reputation metrics. "
        "Requires either agent_id or agent_id_key. "
        "Returns trust_score, reliability_score, coherence_index, and endorsement_count."
    ),
    args_schema=TrustScoreInput,
)


def _trust_attest_sync(input_data: TrustAttestInput) -> dict[str, Any]:
    """Submit trust attestation (sync)."""
    client = EthysClient()
    request = TrustAttestRequest(
        agent_id=input_data.agent_id,
        target_agent_id=input_data.target_agent_id,
        interaction_type=input_data.interaction_type,
        rating=input_data.rating,
        notes=input_data.notes,
    )
    response = client.post("/api/v1/402/trust/attest", data=request.model_dump(by_alias=True))
    attest_response = TrustAttestResponse(**response)
    return {
        "success": attest_response.success,
        "message": attest_response.message,
        "attestation_id": attest_response.attestation_id,
    }


async def _trust_attest_async(input_data: TrustAttestInput) -> dict[str, Any]:
    """Submit trust attestation (async)."""
    client = EthysClient()
    request = TrustAttestRequest(
        agent_id=input_data.agent_id,
        target_agent_id=input_data.target_agent_id,
        interaction_type=input_data.interaction_type,
        rating=input_data.rating,
        notes=input_data.notes,
    )
    response = await client.apost("/api/v1/402/trust/attest", data=request.model_dump(by_alias=True))
    attest_response = TrustAttestResponse(**response)
    return {
        "success": attest_response.success,
        "message": attest_response.message,
        "attestation_id": attest_response.attestation_id,
    }


EthysTrustAttestTool = StructuredTool.from_function(
    func=_trust_attest_sync,
    coroutine=_trust_attest_async,
    name="ethys_trust_attest",
    description=(
        "Submit trust attestation for an interaction with another agent. "
        "Requires: agent_id, target_agent_id, interaction_type, "
        "and optionally rating (1-5) and notes. "
        "Returns success status and attestation_id."
    ),
    args_schema=TrustAttestInput,
)


def _reviews_submit_sync(input_data: ReviewsSubmitInput) -> dict[str, Any]:
    """Submit review (sync)."""
    if input_data.rating < 1 or input_data.rating > 5:
        raise ValidationError("rating must be between 1 and 5")
    client = EthysClient()
    request = ReviewsSubmitRequest(
        agent_id=input_data.agent_id,
        rating=input_data.rating,
        review_text=input_data.review_text,
        signature=input_data.signature,
        domain=input_data.domain,
        types=input_data.types,
        message=input_data.message,
    )
    response = client.post("/api/v1/402/reviews/submit", data=request.model_dump(by_alias=True))
    reviews_response = ReviewsSubmitResponse(**response)
    return {
        "success": reviews_response.success,
        "message": reviews_response.message,
        "review_id": reviews_response.review_id,
    }


async def _reviews_submit_async(input_data: ReviewsSubmitInput) -> dict[str, Any]:
    """Submit review (async)."""
    if input_data.rating < 1 or input_data.rating > 5:
        raise ValidationError("rating must be between 1 and 5")
    client = EthysClient()
    request = ReviewsSubmitRequest(
        agent_id=input_data.agent_id,
        rating=input_data.rating,
        review_text=input_data.review_text,
        signature=input_data.signature,
        domain=input_data.domain,
        types=input_data.types,
        message=input_data.message,
    )
    response = await client.apost("/api/v1/402/reviews/submit", data=request.model_dump(by_alias=True))
    reviews_response = ReviewsSubmitResponse(**response)
    return {
        "success": reviews_response.success,
        "message": reviews_response.message,
        "review_id": reviews_response.review_id,
    }


EthysReviewsSubmitTool = StructuredTool.from_function(
    func=_reviews_submit_sync,
    coroutine=_reviews_submit_async,
    name="ethys_reviews_submit",
    description=(
        "Submit a client review with EIP-712 signature. "
        "Requires: agent_id (being reviewed), rating (1-5), signature (EIP-712), "
        "and optionally review_text, domain, types, message (EIP-712 components). "
        "Returns success status and review_id."
    ),
    args_schema=ReviewsSubmitInput,
)

