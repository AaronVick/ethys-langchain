"""Example: Discovery search and trust scoring with LangChain."""

from langchain_ethys402 import (
    EthysDiscoverySearchTool,
    EthysTrustScoreTool,
    EthysTrustAttestTool,
)


def main() -> None:
    """Example workflow: discovery search and trust operations."""
    print("=== ETHYS Discovery and Trust Example ===\n")

    # Step 1: Search for agents
    print("Step 1: Searching for agents...")
    search_tool = EthysDiscoverySearchTool()
    search_result = search_tool.run(
        {
            "query": "data processing",
            "min_trust_score": 600,
            "service_types": "nlp,data",
            "limit": 5,
        }
    )

    if search_result["success"]:
        agents = search_result["agents"]
        print(f"✅ Found {len(agents)} agents\n")
        for i, agent in enumerate(agents, 1):
            print(f"   {i}. {agent.get('name', 'Unknown')}")
            print(f"      Agent ID: {agent.get('agent_id', 'N/A')}")
            print(f"      Trust Score: {agent.get('trust_score', 'N/A')}")
            print(f"      Services: {', '.join(agent.get('service_types', []))}")
            print()
    else:
        print("❌ Search failed")
        return

    # Step 2: Get detailed trust score for an agent
    if agents:
        print("Step 2: Getting detailed trust score...")
        agent_id = agents[0].get("agent_id")
        if agent_id:
            trust_tool = EthysTrustScoreTool()
            trust_result = trust_tool.run({"agent_id": agent_id})

            if trust_result["success"]:
                print(f"✅ Trust Score Details:")
                print(f"   Trust Score: {trust_result.get('trust_score', 'N/A')}")
                print(f"   Reliability Score: {trust_result.get('reliability_score', 'N/A')}")
                print(f"   Coherence Index: {trust_result.get('coherence_index', 'N/A')}")
                print(f"   Endorsements: {trust_result.get('endorsement_count', 'N/A')}\n")
            else:
                print("❌ Failed to get trust score\n")

    # Step 3: Submit trust attestation (example)
    print("Step 3: Submitting trust attestation...")
    print("   (This is an example - in production, use after actual interaction)")
    attest_tool = EthysTrustAttestTool()
    # Note: This would require actual agent IDs from a real interaction
    print("   ⚠️  Skipping attestation (requires real agent IDs from interaction)")


if __name__ == "__main__":
    main()

