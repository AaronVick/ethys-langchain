"""Authentication and identity encoding for ETHYS x402."""

from typing import Any

from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak, to_hex

from langchain_ethys402.errors import ValidationError
from langchain_ethys402.types import AgentIdentity


def encode_agent_identity(identity: AgentIdentity) -> bytes:
    """Encode AgentIdentity struct using ABI encoding.

    According to x402.json:
    - encoding: "AgentIdentity struct with versioned abi.encode"
    - keying: "agentIdKey = keccak256(abi.encode(AgentIdentity))"

    For EOA: identity_type=1, address=wallet, token_id=0
    For ERC-6551: identity_type=2, address=tokenContract, token_id=tokenId

    Args:
        identity: AgentIdentity instance

    Returns:
        ABI-encoded bytes
    """
    if identity.identity_type == "EOA":
        # EOA: encode as (uint8 version, uint8 type=1, address wallet, uint256 tokenId=0)
        version = identity.version.to_bytes(1, "big")
        identity_type = (1).to_bytes(1, "big")
        address_bytes = bytes.fromhex(identity.address[2:])  # Remove 0x prefix
        token_id = (0).to_bytes(32, "big")
        return version + identity_type + address_bytes + token_id
    elif identity.identity_type == "ERC6551":
        # ERC-6551: encode as (uint8 version, uint8 type=2, address tokenContract, uint256 tokenId)
        version = identity.version.to_bytes(1, "big")
        identity_type = (2).to_bytes(1, "big")
        address_bytes = bytes.fromhex(identity.address[2:])  # Remove 0x prefix
        token_id_bytes = identity.token_id.to_bytes(32, "big") if identity.token_id else (0).to_bytes(32, "big")
        return version + identity_type + address_bytes + token_id_bytes
    else:
        raise ValidationError(f"Unsupported identity type: {identity.identity_type}")


def derive_agent_id_key(identity: AgentIdentity) -> str:
    """Derive agentIdKey from AgentIdentity using keccak256.

    According to x402.json:
    - keying: "agentIdKey = keccak256(abi.encode(AgentIdentity))"

    Args:
        identity: AgentIdentity instance

    Returns:
        Hex string of the keccak256 hash (0x-prefixed, 66 chars)
    """
    encoded = encode_agent_identity(identity)
    hash_bytes = keccak(encoded)
    return to_hex(hash_bytes)


def create_eoa_identity(address: str, version: int = 1) -> AgentIdentity:
    """Create EOA identity from wallet address.

    Args:
        address: Ethereum wallet address
        version: Identity version (default: 1)

    Returns:
        AgentIdentity instance
    """
    return AgentIdentity(
        version=version,
        identity_type="EOA",
        address=address,
        token_id=None,
    )


def create_erc6551_identity(token_contract: str, token_id: int, version: int = 1) -> AgentIdentity:
    """Create ERC-6551 identity from token contract and ID.

    Args:
        token_contract: ERC-6551 token contract address
        token_id: Token ID
        version: Identity version (default: 1)

    Returns:
        AgentIdentity instance
    """
    return AgentIdentity(
        version=version,
        identity_type="ERC6551",
        address=token_contract,
        token_id=token_id,
    )


def sign_message(message: str, private_key: str) -> str:
    """Sign a message with a private key.

    Args:
        message: Message to sign
        private_key: Private key (hex string with or without 0x prefix)

    Returns:
        Signature hex string (0x-prefixed, 132 chars)
    """
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key

    account = Account.from_key(private_key)
    message_encoded = encode_defunct(text=message)
    signed = account.sign_message(message_encoded)
    return "0x" + signed.signature.hex()


def verify_signature(message: str, signature: str, address: str) -> bool:
    """Verify a message signature.

    Args:
        message: Original message
        signature: Signature hex string
        address: Expected signer address

    Returns:
        True if signature is valid
    """
    try:
        message_encoded = encode_defunct(text=message)
        recovered = Account.recover_message(message_encoded, signature=signature)
        return recovered.lower() == address.lower()
    except Exception:
        return False


def generate_nonce() -> str:
    """Generate a 32-byte hex nonce for telemetry requests.

    Returns:
        Hex string (0x-prefixed, 66 chars)
    """
    import secrets

    nonce_bytes = secrets.token_bytes(32)
    return to_hex(nonce_bytes)


def prepare_telemetry_message(
    agent_id: str,
    address: str,
    timestamp: int,
    nonce: str,
    events: list[dict[str, Any]],
) -> str:
    """Prepare message for telemetry signature.

    According to TELEMETRY_WALLET_AUTH_GUIDE.md, the message format should be:
    A structured message containing all fields that will be in the request body.

    Args:
        agent_id: Agent ID
        address: Wallet address
        timestamp: Unix timestamp
        nonce: 32-byte hex nonce
        events: List of telemetry events

    Returns:
        Message string to sign
    """
    import json

    # Create a deterministic JSON representation
    payload = {
        "agentId": agent_id,
        "address": address.lower(),
        "ts": timestamp,
        "nonce": nonce,
        "events": events,
    }
    # Sort keys for deterministic output
    message = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return message


def sign_telemetry_request(
    agent_id: str,
    address: str,
    timestamp: int,
    nonce: str,
    events: list[dict[str, Any]],
    private_key: str,
) -> str:
    """Sign a telemetry request.

    Args:
        agent_id: Agent ID
        address: Wallet address
        timestamp: Unix timestamp
        nonce: 32-byte hex nonce
        events: List of telemetry events
        private_key: Private key for signing

    Returns:
        Signature hex string
    """
    message = prepare_telemetry_message(agent_id, address, timestamp, nonce, events)
    return sign_message(message, private_key)

