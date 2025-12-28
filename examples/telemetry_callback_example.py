"""Example: Using telemetry callback handler (opt-in)."""

import os

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from langchain_ethys402 import (
    EthysGetInfoTool,
    EthysTelemetryCallbackHandler,
)


def main() -> None:
    """Example: Using telemetry callback handler."""
    print("=== ETHYS Telemetry Callback Example ===\n")

    # WARNING: Telemetry callback is opt-in and requires explicit configuration
    # Never enable by default. Requires agent_id, wallet address, and private key.

    agent_id = os.getenv("ETHYS_AGENT_ID", "")
    wallet_address = os.getenv("ETHYS_WALLET_ADDRESS", "")
    private_key = os.getenv("ETHYS_PRIVATE_KEY", "")

    if not all([agent_id, wallet_address, private_key]):
        print("❌ Missing required environment variables:")
        print("   - ETHYS_AGENT_ID")
        print("   - ETHYS_WALLET_ADDRESS")
        print("   - ETHYS_PRIVATE_KEY")
        print("\n⚠️  Telemetry callback is opt-in and requires explicit configuration.")
        print("   Set these variables to enable telemetry submission.")
        return

    # Create telemetry callback (opt-in, must be explicitly enabled)
    callback = EthysTelemetryCallbackHandler(
        agent_id=agent_id,
        address=wallet_address,
        private_key=private_key,
        enabled=True,  # Must be explicitly enabled
        batch_size=5,  # Send telemetry every 5 events
    )

    print("✅ Telemetry callback configured")
    print(f"   Agent ID: {agent_id}")
    print(f"   Batch size: {callback.batch_size}\n")

    # Create agent with tools
    tools = [EthysGetInfoTool()]
    llm = ChatOpenAI(temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant with access to ETHYS tools."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[callback],  # Add callback here
        verbose=True,
    )

    # Run agent - telemetry will be automatically submitted
    print("Running agent (telemetry will be submitted automatically)...\n")
    result = agent_executor.invoke(
        {"input": "Get ETHYS protocol information"},
    )

    print("\n✅ Agent execution complete")
    print(f"   Result: {result.get('output', 'N/A')[:100]}...\n")

    # Manually flush any pending telemetry events
    print("Flushing pending telemetry events...")
    callback.flush()
    print("✅ Telemetry flush complete")


if __name__ == "__main__":
    main()

