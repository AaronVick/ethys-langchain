"""Tests for auth module."""

import pytest

from langchain_ethys402.auth import (
    create_eoa_identity,
    create_erc6551_identity,
    derive_agent_id_key,
    generate_nonce,
    sign_message,
    verify_signature,
)
from langchain_ethys402.types import AgentIdentity


def test_create_eoa_identity() -> None:
    """Test creating EOA identity."""
    identity = create_eoa_identity("0x1234567890123456789012345678901234567890")
    assert identity.identity_type == "EOA"
    assert identity.address == "0x1234567890123456789012345678901234567890"
    assert identity.token_id is None
    assert identity.version == 1


def test_create_erc6551_identity() -> None:
    """Test creating ERC-6551 identity."""
    identity = create_erc6551_identity(
        "0x1234567890123456789012345678901234567890", token_id=123
    )
    assert identity.identity_type == "ERC6551"
    assert identity.address == "0x1234567890123456789012345678901234567890"
    assert identity.token_id == 123
    assert identity.version == 1


def test_encode_agent_identity_eoa() -> None:
    """Test encoding EOA identity."""
    identity = create_eoa_identity("0x1234567890123456789012345678901234567890")
    encoded = encode_agent_identity(identity)
    assert isinstance(encoded, bytes)
    assert len(encoded) > 0


def test_encode_agent_identity_erc6551() -> None:
    """Test encoding ERC-6551 identity."""
    identity = create_erc6551_identity(
        "0x1234567890123456789012345678901234567890", token_id=123
    )
    encoded = encode_agent_identity(identity)
    assert isinstance(encoded, bytes)
    assert len(encoded) > 0


def test_derive_agent_id_key() -> None:
    """Test deriving agent ID key."""
    identity = create_eoa_identity("0x1234567890123456789012345678901234567890")
    key = derive_agent_id_key(identity)
    assert isinstance(key, str)
    assert key.startswith("0x")
    assert len(key) == 66  # 0x + 64 hex chars


def test_derive_agent_id_key_deterministic() -> None:
    """Test that agent ID key is deterministic."""
    identity1 = create_eoa_identity("0x1234567890123456789012345678901234567890")
    identity2 = create_eoa_identity("0x1234567890123456789012345678901234567890")
    key1 = derive_agent_id_key(identity1)
    key2 = derive_agent_id_key(identity2)
    assert key1 == key2


def test_generate_nonce() -> None:
    """Test nonce generation."""
    nonce = generate_nonce()
    assert isinstance(nonce, str)
    assert nonce.startswith("0x")
    assert len(nonce) == 66  # 0x + 64 hex chars


def test_generate_nonce_unique() -> None:
    """Test that nonces are unique."""
    nonces = {generate_nonce() for _ in range(100)}
    assert len(nonces) == 100  # All should be unique


def test_sign_and_verify_message() -> None:
    """Test signing and verifying a message."""
    # Use a test private key (DO NOT USE IN PRODUCTION)
    private_key = "0x" + "1" * 64
    message = "Test message"
    signature = sign_message(message, private_key)
    assert isinstance(signature, str)
    assert len(signature) == 132  # 0x + 130 hex chars

    # Verify signature
    from eth_account import Account

    account = Account.from_key(private_key)
    is_valid = verify_signature(message, signature, account.address)
    assert is_valid


def test_invalid_identity_type() -> None:
    """Test that invalid identity type raises error."""
    from pydantic import ValidationError

    # Pydantic validator catches invalid identity_type during model creation
    with pytest.raises(ValidationError):
        AgentIdentity(
            version=1, identity_type="INVALID", address="0x1234567890123456789012345678901234567890"
        )

