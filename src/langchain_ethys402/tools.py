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
    tx_hash: Optional[str] = Field(None, description="Transaction hash (optional)")


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


# --- Get Info Tool ---
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


# --- Connect Tool ---
def _connect_sync(address: str, signature: str, message: str) -> dict[str, Any]:
    """Connect agent (sync)."""
    client = EthysClient()
    request = ConnectRequest(address=address, signature=signature, message=message)
    response = client.post("/api/v1/402/connect", data=request.model_dump(by_alias=True))
    connect_response = ConnectResponse(**response)
    return {
        "success": connect_response.success,
        "agent_id": connect_response.agent_id,
        "agent_id_key": connect_response.agent_id_key,
        "onboarding": connect_response.onboarding,
    }


async def _connect_async(address: str, signature: str, message: str) -> dict[str, Any]:
    """Connect agent (async)."""
    client = EthysClient()
    request = ConnectRequest(address=address, signature=signature, message=message)
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


# --- Verify Payment Tool ---
def _verify_payment_sync(agent_id: str, tx_hash: Optional[str] = None) -> dict[str, Any]:
    """Verify payment (sync)."""
    client = EthysClient()
    request = VerifyPaymentRequest(agent_id=agent_id, tx_hash=tx_hash)
    response = client.post("/api/v1/402/verify-payment", data=request.model_dump(by_alias=True))
    verify_response = VerifyPaymentResponse(**response)
    return {
        "success": verify_response.success,
        "message": verify_response.message,
        "agent_id": verify_response.agent_id,
        "api_key": verify_response.api_key,
    }


async def _verify_payment_async(agent_id: str, tx_hash: Optional[str] = None) -> dict[str, Any]:
    """Verify payment (async)."""
    client = EthysClient()
    request = VerifyPaymentRequest(agent_id=agent_id, tx_hash=tx_hash)
    response = await client.apost(
        "/api/v1/402/verify-payment", data=request.model_dump(by_alias=True)
    )
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
        "Verify ETHYS payment transaction after calling buyTierAuto() on the contract. "
        "Requires: agent_id (from connect) and optionally tx_hash (transaction hash). "
        "Returns success status and API key if payment is verified."
    ),
    args_schema=VerifyPaymentInput,
)


# --- Telemetry Tool ---
def _telemetry_sync(
    agent_id: str,
    address: str,
    timestamp: int,
    nonce: str,
    events: list[dict[str, Any]],
    signature: str,
) -> dict[str, Any]:
    """Submit telemetry (sync)."""
    client = EthysClient()
    telemetry_events = [TelemetryEvent(**event) for event in events]
    request = TelemetryRequest(
        agent_id=agent_id,
        address=address,
        ts=timestamp,
        nonce=nonce,
        events=[e.model_dump(by_alias=True) for e in telemetry_events],
        signature=signature,
    )
    response = client.post("/api/v1/402/telemetry", data=request.model_dump(by_alias=True))
    telemetry_response = TelemetryResponse(**response)
    return {
        "success": telemetry_response.success,
        "message": telemetry_response.message,
        "events_processed": telemetry_response.events_processed,
    }


async def _telemetry_async(
    agent_id: str,
    address: str,
    timestamp: int,
    nonce: str,
    events: list[dict[str, Any]],
    signature: str,
) -> dict[str, Any]:
    """Submit telemetry (async)."""
    client = EthysClient()
    telemetry_events = [TelemetryEvent(**event) for event in events]
    request = TelemetryRequest(
        agent_id=agent_id,
        address=address,
        ts=timestamp,
        nonce=nonce,
        events=[e.model_dump(by_alias=True) for e in telemetry_events],
        signature=signature,
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


# --- Discovery Search Tool ---
def _discovery_search_sync(
    query: Optional[str] = None,
    min_trust_score: Optional[int] = None,
    service_types: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> dict[str, Any]:
    """Search discovery (sync)."""
    client = EthysClient()
    params = DiscoverySearchParams(
        query=query,
        min_trust_score=min_trust_score,
        service_types=service_types,
        limit=limit,
        offset=offset,
    )
    query_params = params.model_dump(by_alias=True, exclude_none=True)
    response = client.get("/api/v1/402/discovery/search", params=query_params)
    search_response = DiscoverySearchResponse(**response)
    return {
        "success": search_response.success,
        "agents": [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "trust_score": agent.trust_score,
                "service_types": agent.service_types,
            }
            for agent in search_response.agents
        ],
        "total": search_response.total,
        "limit": search_response.limit,
        "offset": search_response.offset,
    }


async def _discovery_search_async(
    query: Optional[str] = None,
    min_trust_score: Optional[int] = None,
    service_types: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> dict[str, Any]:
    """Search discovery (async)."""
    client = EthysClient()
    params = DiscoverySearchParams(
        query=query,
        min_trust_score=min_trust_score,
        service_types=service_types,
        limit=limit,
        offset=offset,
    )
    query_params = params.model_dump(by_alias=True, exclude_none=True)
    response = await client.aget("/api/v1/402/discovery/search", params=query_params)
    search_response = DiscoverySearchResponse(**response)
    return {
        "success": search_response.success,
        "agents": [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "trust_score": agent.trust_score,
                "service_types": agent.service_types,
            }
            for agent in search_response.agents
        ],
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
        "Optional parameters: query (search string), min_trust_score (minimum score), "
        "service_types (comma-separated list), limit (max results), offset (pagination). "
        "Returns list of matching agents with their trust scores and capabilities."
    ),
    args_schema=DiscoverySearchInput,
)


# --- Trust Score Tool ---
def _trust_score_sync(
    agent_id: Optional[str] = None, agent_id_key: Optional[str] = None
) -> dict[str, Any]:
    """Get trust score (sync)."""
    if not agent_id and not agent_id_key:
        raise ValidationError("Either agent_id or agent_id_key must be provided")
    client = EthysClient()
    params = TrustScoreRequest(agent_id=agent_id, agent_id_key=agent_id_key)
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


async def _trust_score_async(
    agent_id: Optional[str] = None, agent_id_key: Optional[str] = None
) -> dict[str, Any]:
    """Get trust score (async)."""
    if not agent_id and not agent_id_key:
        raise ValidationError("Either agent_id or agent_id_key must be provided")
    client = EthysClient()
    params = TrustScoreRequest(agent_id=agent_id, agent_id_key=agent_id_key)
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


# --- Trust Attest Tool ---
def _trust_attest_sync(
    agent_id: str,
    target_agent_id: str,
    interaction_type: str,
    rating: Optional[int] = None,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """Submit trust attestation (sync)."""
    client = EthysClient()
    request = TrustAttestRequest(
        agent_id=agent_id,
        target_agent_id=target_agent_id,
        interaction_type=interaction_type,
        rating=rating,
        notes=notes,
    )
    response = client.post("/api/v1/402/trust/attest", data=request.model_dump(by_alias=True))
    attest_response = TrustAttestResponse(**response)
    return {
        "success": attest_response.success,
        "message": attest_response.message,
        "attestation_id": attest_response.attestation_id,
    }


async def _trust_attest_async(
    agent_id: str,
    target_agent_id: str,
    interaction_type: str,
    rating: Optional[int] = None,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    """Submit trust attestation (async)."""
    client = EthysClient()
    request = TrustAttestRequest(
        agent_id=agent_id,
        target_agent_id=target_agent_id,
        interaction_type=interaction_type,
        rating=rating,
        notes=notes,
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


# --- Reviews Submit Tool ---
def _reviews_submit_sync(
    agent_id: str,
    rating: int,
    signature: str,
    review_text: Optional[str] = None,
    domain: Optional[dict[str, Any]] = None,
    types: Optional[dict[str, Any]] = None,
    message: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Submit review (sync)."""
    if rating < 1 or rating > 5:
        raise ValidationError("rating must be between 1 and 5")
    client = EthysClient()
    request = ReviewsSubmitRequest(
        agent_id=agent_id,
        rating=rating,
        review_text=review_text,
        signature=signature,
        domain=domain,
        types=types,
        message=message,
    )
    response = client.post("/api/v1/402/reviews/submit", data=request.model_dump(by_alias=True))
    reviews_response = ReviewsSubmitResponse(**response)
    return {
        "success": reviews_response.success,
        "message": reviews_response.message,
        "review_id": reviews_response.review_id,
    }


async def _reviews_submit_async(
    agent_id: str,
    rating: int,
    signature: str,
    review_text: Optional[str] = None,
    domain: Optional[dict[str, Any]] = None,
    types: Optional[dict[str, Any]] = None,
    message: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Submit review (async)."""
    if rating < 1 or rating > 5:
        raise ValidationError("rating must be between 1 and 5")
    client = EthysClient()
    request = ReviewsSubmitRequest(
        agent_id=agent_id,
        rating=rating,
        review_text=review_text,
        signature=signature,
        domain=domain,
        types=types,
        message=message,
    )
    response = await client.apost(
        "/api/v1/402/reviews/submit", data=request.model_dump(by_alias=True)
    )
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
