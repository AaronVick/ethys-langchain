"""Configuration management for ETHYS x402 integration."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables from .env file
load_dotenv()


class EthysConfig(BaseModel):
    """Configuration for ETHYS x402 client."""

    base_url: str = Field(
        default="https://402.ethys.dev",
        description="Base URL for ETHYS API",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (optional, wallet signature preferred)",
    )
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests",
    )
    chain_id: int = Field(
        default=8453,
        description="Chain ID (Base mainnet: 8453)",
    )
    ethys_token_address: str = Field(
        default="0x1Dd996287dB5a95D6C9236EfB10C7f90145e5B07",
        description="ETHYS token contract address",
    )
    tier_purchase_v1_address: str = Field(
        default="0x5BA13d7183603cB42240a80Fe76A73D7750287Ec",
        description="V1 tier purchase contract address",
    )
    tier_purchase_v2_address: str = Field(
        default="0x1AB4434AF31AF4b8564c4bB12B6aD417B97923b8",
        description="V2 tier purchase contract address",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")

    @classmethod
    def from_env(cls) -> "EthysConfig":
        """Create config from environment variables."""
        return cls(
            base_url=os.getenv("ETHYS_BASE_URL", "https://402.ethys.dev"),
            api_key=os.getenv("ETHYS_API_KEY"),
            timeout=float(os.getenv("ETHYS_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("ETHYS_MAX_RETRIES", "3")),
            chain_id=int(os.getenv("ETHYS_CHAIN_ID", "8453")),
            ethys_token_address=os.getenv(
                "ETHYS_TOKEN_ADDRESS",
                "0x1Dd996287dB5a95D6C9236EfB10C7f90145e5B07",
            ),
            tier_purchase_v1_address=os.getenv(
                "ETHYS_TIER_PURCHASE_V1_ADDRESS",
                "0x5BA13d7183603cB42240a80Fe76A73D7750287Ec",
            ),
            tier_purchase_v2_address=os.getenv(
                "ETHYS_TIER_PURCHASE_V2_ADDRESS",
                "0x1AB4434AF31AF4b8564c4bB12B6aD417B97923b8",
            ),
        )

