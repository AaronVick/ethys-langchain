"""HTTP client for ETHYS x402 API."""

import json
from typing import Any, Optional

import httpx

from langchain_ethys402.config import EthysConfig
from langchain_ethys402.errors import ApiError, NetworkError, TimeoutError


class EthysClient:
    """HTTP client for ETHYS x402 API with sync and async support."""

    def __init__(self, config: Optional[EthysConfig] = None) -> None:
        """Initialize client with configuration.

        Args:
            config: EthysConfig instance (defaults to from_env())
        """
        self.config = config or EthysConfig.from_env()
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    def _get_sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client."""
        if self._sync_client is None:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            self._sync_client = httpx.Client(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            self._async_client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        return self._async_client

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate errors.

        Args:
            response: httpx.Response instance

        Returns:
            Parsed JSON response

        Raises:
            ApiError: For API errors
            NetworkError: For network errors
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Try to parse error response
            try:
                error_body = response.json()
            except Exception:
                error_body = {"error": response.text}
            raise ApiError(
                message=f"API error: {e.response.status_code}",
                status_code=e.response.status_code,
                response_body=error_body,
            ) from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}") from e

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise ApiError(
                message="Invalid JSON response",
                status_code=response.status_code,
                response_body={"raw": response.text},
            ) from e

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make synchronous GET request.

        Args:
            path: API path (e.g., "/api/v1/402/info")
            params: Query parameters

        Returns:
            Parsed JSON response
        """
        client = self._get_sync_client()
        try:
            response = client.get(path, params=params)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {path}", timeout=self.config.timeout) from e

    async def aget(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make asynchronous GET request.

        Args:
            path: API path (e.g., "/api/v1/402/info")
            params: Query parameters

        Returns:
            Parsed JSON response
        """
        client = self._get_async_client()
        try:
            response = await client.get(path, params=params)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {path}", timeout=self.config.timeout) from e

    def post(
        self,
        path: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Make synchronous POST request.

        Args:
            path: API path
            data: Request body
            headers: Additional headers

        Returns:
            Parsed JSON response
        """
        client = self._get_sync_client()
        request_headers = dict(client.headers)
        if headers:
            request_headers.update(headers)
        try:
            response = client.post(path, json=data, headers=request_headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {path}", timeout=self.config.timeout) from e

    async def apost(
        self,
        path: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Make asynchronous POST request.

        Args:
            path: API path
            data: Request body
            headers: Additional headers

        Returns:
            Parsed JSON response
        """
        client = self._get_async_client()
        request_headers = dict(client.headers)
        if headers:
            request_headers.update(headers)
        try:
            response = await client.post(path, json=data, headers=request_headers)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {path}", timeout=self.config.timeout) from e

    def close(self) -> None:
        """Close sync client."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def aclose(self) -> None:
        """Close async client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> "EthysClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "EthysClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.aclose()

