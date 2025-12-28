"""Pydantic v2 models for ETHYS x402 API types."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# Identity types
class AgentIdentity(BaseModel):
    """Agent identity structure for EOA or ERC-6551."""

    version: int = Field(default=1, description="Identity version")
    identity_type: str = Field(..., description="Identity type: 'EOA' or 'ERC6551'")
    address: str = Field(..., description="Wallet address (EOA) or token contract (ERC-6551)")
    token_id: Optional[int] = Field(None, description="Token ID for ERC-6551")

    @field_validator("identity_type")
    @classmethod
    def validate_identity_type(cls, v: str) -> str:
        """Validate identity type."""
        if v not in ("EOA", "ERC6551"):
            raise ValueError("identity_type must be 'EOA' or 'ERC6551'")
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address format."""
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("address must be a valid Ethereum address (0x followed by 40 hex chars)")
        return v.lower()


# Connect request/response
class ConnectRequest(BaseModel):
    """Request for POST /api/v1/402/connect."""

    address: str = Field(..., description="Wallet address")
    signature: str = Field(..., description="Wallet signature of the message")
    message: str = Field(..., description="Message that was signed")


class ConnectResponse(BaseModel):
    """Response from POST /api/v1/402/connect."""

    success: bool
    agent_id: Optional[str] = Field(None, alias="agentId")
    onboarding: Optional[dict[str, Any]] = None
    agent_id_key: Optional[str] = Field(None, alias="agentIdKey")

    class Config:
        populate_by_name = True


# Verify payment request/response
class VerifyPaymentRequest(BaseModel):
    """Request for POST /api/v1/402/verify-payment."""

    agent_id: str = Field(..., alias="agentId", description="Agent ID from connect")
    tx_hash: Optional[str] = Field(None, alias="txHash", description="Transaction hash (optional)")

    class Config:
        populate_by_name = True


class VerifyPaymentResponse(BaseModel):
    """Response from POST /api/v1/402/verify-payment."""

    success: bool
    message: Optional[str] = None
    agent_id: Optional[str] = Field(None, alias="agentId")
    api_key: Optional[str] = Field(None, alias="apiKey")

    class Config:
        populate_by_name = True


# Telemetry request/response
class TelemetryEvent(BaseModel):
    """Single telemetry event."""

    event_type: str = Field(..., alias="eventType", description="Event type identifier")
    timestamp: int = Field(..., description="Unix timestamp")
    data: dict[str, Any] = Field(default_factory=dict, description="Event data")

    class Config:
        populate_by_name = True


class TelemetryRequest(BaseModel):
    """Request for POST /api/v1/402/telemetry."""

    agent_id: str = Field(..., alias="agentId", description="Agent ID")
    address: str = Field(..., description="Wallet address")
    ts: int = Field(..., description="Unix timestamp")
    nonce: str = Field(..., description="32-byte hex nonce")
    events: list[TelemetryEvent] = Field(..., description="List of telemetry events")
    signature: str = Field(..., description="Wallet signature of the payload")

    class Config:
        populate_by_name = True


class TelemetryResponse(BaseModel):
    """Response from POST /api/v1/402/telemetry."""

    success: bool
    message: Optional[str] = None
    events_processed: Optional[int] = Field(None, alias="eventsProcessed")


# Discovery search request/response
class DiscoverySearchParams(BaseModel):
    """Parameters for GET /api/v1/402/discovery/search."""

    query: Optional[str] = Field(None, description="Search query string")
    min_trust_score: Optional[int] = Field(None, alias="minTrustScore", description="Minimum trust score")
    service_types: Optional[str] = Field(None, alias="serviceTypes", description="Comma-separated service types")
    limit: Optional[int] = Field(None, description="Maximum number of results")
    offset: Optional[int] = Field(None, description="Pagination offset")

    class Config:
        populate_by_name = True


class DiscoveryAgent(BaseModel):
    """Agent in discovery search results."""

    agent_id: str = Field(..., alias="agentId")
    agent_id_key: Optional[str] = Field(None, alias="agentIdKey")
    name: Optional[str] = None
    description: Optional[str] = None
    trust_score: Optional[int] = Field(None, alias="trustScore")
    service_types: Optional[list[str]] = Field(None, alias="serviceTypes")
    capabilities: Optional[dict[str, Any]] = None

    class Config:
        populate_by_name = True


class DiscoverySearchResponse(BaseModel):
    """Response from GET /api/v1/402/discovery/search."""

    success: bool
    agents: list[DiscoveryAgent] = Field(default_factory=list)
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


# Trust score request/response
class TrustScoreRequest(BaseModel):
    """Parameters for GET /api/v1/402/trust/score."""

    agent_id: Optional[str] = Field(None, alias="agentId", description="Agent ID")
    agent_id_key: Optional[str] = Field(None, alias="agentIdKey", description="Agent ID key (bytes32)")

    class Config:
        populate_by_name = True


class TrustScoreResponse(BaseModel):
    """Response from GET /api/v1/402/trust/score."""

    success: bool
    agent_id: Optional[str] = Field(None, alias="agentId")
    agent_id_key: Optional[str] = Field(None, alias="agentIdKey")
    trust_score: Optional[int] = Field(None, alias="trustScore")
    reliability_score: Optional[float] = Field(None, alias="reliabilityScore")
    coherence_index: Optional[float] = Field(None, alias="coherenceIndex")
    endorsement_count: Optional[int] = Field(None, alias="endorsementCount")

    class Config:
        populate_by_name = True


# Trust attest request/response
class TrustAttestRequest(BaseModel):
    """Request for POST /api/v1/402/trust/attest."""

    agent_id: str = Field(..., alias="agentId", description="Agent ID")
    target_agent_id: str = Field(..., alias="targetAgentId", description="Target agent ID")
    interaction_type: str = Field(..., alias="interactionType", description="Type of interaction")
    rating: Optional[int] = Field(None, description="Rating (1-5)")
    notes: Optional[str] = Field(None, description="Optional notes")

    class Config:
        populate_by_name = True


class TrustAttestResponse(BaseModel):
    """Response from POST /api/v1/402/trust/attest."""

    success: bool
    message: Optional[str] = None
    attestation_id: Optional[str] = Field(None, alias="attestationId")


# Reviews submit request/response
class ReviewsSubmitRequest(BaseModel):
    """Request for POST /api/v1/402/reviews/submit."""

    agent_id: str = Field(..., alias="agentId", description="Agent ID being reviewed")
    rating: int = Field(..., description="Rating (1-5)")
    review_text: Optional[str] = Field(None, alias="reviewText", description="Review text")
    signature: str = Field(..., description="EIP-712 signature")
    domain: Optional[dict[str, Any]] = Field(None, description="EIP-712 domain")
    types: Optional[dict[str, Any]] = Field(None, description="EIP-712 types")
    message: Optional[dict[str, Any]] = Field(None, description="EIP-712 message")

    class Config:
        populate_by_name = True


class ReviewsSubmitResponse(BaseModel):
    """Response from POST /api/v1/402/reviews/submit."""

    success: bool
    message: Optional[str] = None
    review_id: Optional[str] = Field(None, alias="reviewId")


# Info response
class InfoResponse(BaseModel):
    """Response from GET /api/v1/402/info."""

    protocol: str
    name: str
    description: str
    version: str
    onboarding: dict[str, Any]
    pricing: dict[str, Any]
    network: dict[str, Any]
    endpoints: dict[str, Any]
    features: list[str] = Field(default_factory=list)

