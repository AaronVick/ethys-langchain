"""LangChain integration for ETHYS x402 framework.

This package provides LangChain Tools, Retrievers, and Callbacks for interacting
with the ETHYS x402 protocol on Base L2.
"""

from langchain_ethys402.callbacks import EthysTelemetryCallbackHandler
from langchain_ethys402.client import EthysClient
from langchain_ethys402.config import EthysConfig
from langchain_ethys402.errors import (
    ApiError,
    AuthError,
    EthysError,
    NetworkError,
    TimeoutError,
    ValidationError,
)
from langchain_ethys402.retrievers import EthysDiscoveryRetriever
from langchain_ethys402.tools import (
    EthysConnectTool,
    EthysDiscoverySearchTool,
    EthysGetInfoTool,
    EthysReviewsSubmitTool,
    EthysTelemetryTool,
    EthysTrustAttestTool,
    EthysTrustScoreTool,
    EthysVerifyPaymentTool,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "EthysClient",
    "EthysConfig",
    # Errors
    "EthysError",
    "AuthError",
    "ValidationError",
    "ApiError",
    "NetworkError",
    "TimeoutError",
    # Tools
    "EthysGetInfoTool",
    "EthysConnectTool",
    "EthysVerifyPaymentTool",
    "EthysTelemetryTool",
    "EthysDiscoverySearchTool",
    "EthysTrustScoreTool",
    "EthysTrustAttestTool",
    "EthysReviewsSubmitTool",
    # Optional components
    "EthysDiscoveryRetriever",
    "EthysTelemetryCallbackHandler",
]

