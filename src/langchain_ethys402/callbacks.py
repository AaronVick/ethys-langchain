"""LangChain Callbacks for ETHYS x402 telemetry."""

import time
from typing import Any, Dict, List, Optional

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from pydantic import Field

from langchain_ethys402.auth import generate_nonce, sign_telemetry_request
from langchain_ethys402.client import EthysClient
from langchain_ethys402.config import EthysConfig
from langchain_ethys402.errors import ValidationError
from langchain_ethys402.types import TelemetryEvent, TelemetryRequest, TelemetryResponse


class EthysTelemetryCallbackHandler(BaseCallbackHandler):
    """Callback handler that automatically submits telemetry to ETHYS.

    This handler is opt-in and must be explicitly enabled. It collects
    LangChain execution events and submits them as telemetry to ETHYS.

    WARNING: Never enable this by default. It requires explicit configuration
    with agent_id, wallet address, and private key.
    """

    agent_id: str = Field(..., description="Agent ID for telemetry")
    address: str = Field(..., description="Wallet address for signing")
    private_key: str = Field(..., description="Private key for signing (keep secure!)")
    client: EthysClient = Field(default_factory=EthysClient)
    enabled: bool = Field(default=True, description="Whether telemetry is enabled")
    batch_size: int = Field(default=10, description="Number of events to batch before sending")

    _events: List[Dict[str, Any]] = Field(default_factory=list, exclude=True)
    _last_send_time: float = Field(default=0.0, exclude=True)

    def __init__(
        self,
        agent_id: str,
        address: str,
        private_key: str,
        enabled: bool = True,
        batch_size: int = 10,
        config: Optional[EthysConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize callback handler.

        Args:
            agent_id: Agent ID for telemetry
            address: Wallet address for signing
            private_key: Private key for signing (keep secure!)
            enabled: Whether telemetry is enabled (default: True)
            batch_size: Number of events to batch before sending
            config: Optional EthysConfig instance
            **kwargs: Additional arguments passed to BaseCallbackHandler
        """
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self.address = address
        self.private_key = private_key
        self.enabled = enabled
        self.batch_size = batch_size
        self.client = EthysClient(config=config) if config else EthysClient()
        self._events = []
        self._last_send_time = 0.0

    def _add_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Add an event to the batch."""
        if not self.enabled:
            return

        event = {
            "eventType": event_type,
            "timestamp": int(time.time()),
            "data": data,
        }
        self._events.append(event)

        # Auto-send if batch size reached
        if len(self._events) >= self.batch_size:
            self._send_telemetry()

    def _send_telemetry(self) -> None:
        """Send batched telemetry events."""
        if not self._events or not self.enabled:
            return

        try:
            timestamp = int(time.time())
            nonce = generate_nonce()

            # Sign the telemetry request
            signature = sign_telemetry_request(
                agent_id=self.agent_id,
                address=self.address,
                timestamp=timestamp,
                nonce=nonce,
                events=self._events,
                private_key=self.private_key,
            )

            # Create request
            telemetry_events = [TelemetryEvent(**event) for event in self._events]
            request = TelemetryRequest(
                agent_id=self.agent_id,
                address=self.address,
                ts=timestamp,
                nonce=nonce,
                events=[e.model_dump(by_alias=True) for e in telemetry_events],
                signature=signature,
            )

            # Send request
            response = self.client.post("/api/v1/402/telemetry", data=request.model_dump(by_alias=True))
            telemetry_response = TelemetryResponse(**response)

            if telemetry_response.success:
                # Clear events on success
                self._events = []
                self._last_send_time = time.time()
            else:
                # Keep events for retry, but log error
                print(f"Warning: Telemetry submission failed: {telemetry_response.message}")
        except Exception as e:
            # Don't raise - telemetry failures shouldn't break the main flow
            print(f"Warning: Failed to send telemetry: {str(e)}")

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Called when LLM starts."""
        self._add_event(
            "llm_start",
            {
                "serialized": serialized,
                "prompt_count": len(prompts),
            },
        )

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends."""
        self._add_event(
            "llm_end",
            {
                "generation_count": len(response.generations) if response.generations else 0,
            },
        )

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM errors."""
        self._add_event(
            "llm_error",
            {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain starts."""
        self._add_event(
            "chain_start",
            {
                "serialized": serialized,
            },
        )

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Called when chain ends."""
        self._add_event(
            "chain_end",
            {
                "output_keys": list(outputs.keys()) if isinstance(outputs, dict) else [],
            },
        )

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when chain errors."""
        self._add_event(
            "chain_error",
            {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Called when tool starts."""
        self._add_event(
            "tool_start",
            {
                "tool": serialized.get("name", "unknown"),
                "input": input_str[:100] if input_str else "",  # Truncate for privacy
            },
        )

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when tool ends."""
        self._add_event(
            "tool_end",
            {
                "output_length": len(output) if output else 0,
            },
        )

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when tool errors."""
        self._add_event(
            "tool_error",
            {
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Called when agent takes an action."""
        self._add_event(
            "agent_action",
            {
                "tool": action.tool,
                "tool_input": str(action.tool_input)[:100] if action.tool_input else "",  # Truncate
            },
        )

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Called when agent finishes."""
        self._add_event(
            "agent_finish",
            {
                "return_values_keys": list(finish.return_values.keys()) if finish.return_values else [],
            },
        )

    def flush(self) -> None:
        """Manually flush any pending telemetry events."""
        self._send_telemetry()

    def __del__(self) -> None:
        """Cleanup: send any pending events."""
        try:
            self.flush()
        except Exception:
            pass  # Ignore errors during cleanup

