"""Example: Connect agent and verify payment with LangChain."""

import os
from langchain_ethys402 import EthysConnectTool, EthysVerifyPaymentTool
from langchain_ethys402.auth import sign_message

# Configuration (in production, use environment variables or secure storage)
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "0x1234567890123456789012345678901234567890")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")  # DO NOT hardcode in production!


def main() -> None:
    """Example workflow: connect and verify payment."""
    print("=== ETHYS Connect and Verify Payment Example ===\n")

    # Step 1: Connect with wallet signature
    print("Step 1: Connecting agent...")
    message = "Sign this message to connect to ETHYS x402 protocol"
    signature = sign_message(message, PRIVATE_KEY)

    connect_tool = EthysConnectTool()
    connect_result = connect_tool.run(
        {
            "address": WALLET_ADDRESS,
            "signature": signature,
            "message": message,
        }
    )

    if not connect_result["success"]:
        print(f"❌ Connection failed: {connect_result}")
        return

    agent_id = connect_result["agent_id"]
    print(f"✅ Connected! Agent ID: {agent_id}")
    print(f"   Agent ID Key: {connect_result.get('agent_id_key', 'N/A')}\n")

    # Step 2: Verify payment (after calling buyTierAuto() on contract)
    print("Step 2: Verifying payment...")
    print("   (In production, you would call buyTierAuto() on the purchase contract first)")
    print("   Transaction hash from buyTierAuto() call: 0x...\n")

    # Example: verify with transaction hash
    tx_hash = os.getenv("PAYMENT_TX_HASH", "")  # From buyTierAuto() call
    if tx_hash:
        verify_tool = EthysVerifyPaymentTool()
        verify_result = verify_tool.run(
            {
                "agent_id": agent_id,
                "tx_hash": tx_hash,
            }
        )

        if verify_result["success"]:
            print(f"✅ Payment verified!")
            print(f"   API Key: {verify_result.get('api_key', 'N/A')}")
        else:
            print(f"❌ Payment verification failed: {verify_result.get('message', 'Unknown error')}")
    else:
        print("   ⚠️  No transaction hash provided. Skipping verification.")
        print("   Set PAYMENT_TX_HASH environment variable to test verification.")


if __name__ == "__main__":
    main()

