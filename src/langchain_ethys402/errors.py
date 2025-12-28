"""Error hierarchy for ETHYS x402 integration."""

from typing import Any, Optional


class EthysError(Exception):
    """Base exception for all ETHYS errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthError(EthysError):
    """Authentication or authorization error."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code


class ValidationError(EthysError):
    """Input validation error."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        field: Optional[str] = None,
    ) -> None:
        super().__init__(message, details)
        self.field = field


class ApiError(EthysError):
    """API error with status code and parsed response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[dict[str, Any]] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body or {}


class NetworkError(EthysError):
    """Network connectivity error."""

    pass


class TimeoutError(EthysError):
    """Request timeout error."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.timeout = timeout

