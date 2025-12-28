"""LangChain Retrievers for ETHYS x402 discovery."""

from typing import Any, List

from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import Field

from langchain_ethys402.client import EthysClient
from langchain_ethys402.types import DiscoverySearchParams, DiscoverySearchResponse


class EthysDiscoveryRetriever(BaseRetriever):
    """Retriever that searches ETHYS agent discovery system.

    Converts discovery search results into LangChain Document format
    for use in retrieval-augmented generation (RAG) pipelines.
    """

    client: EthysClient = Field(default_factory=EthysClient)
    min_trust_score: int = Field(default=0, description="Minimum trust score filter")
    service_types: str = Field(default="", description="Comma-separated service types filter")
    limit: int = Field(default=10, description="Maximum number of results")

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents synchronously."""
        params = DiscoverySearchParams(
            query=query,
            min_trust_score=self.min_trust_score if self.min_trust_score > 0 else None,
            service_types=self.service_types if self.service_types else None,
            limit=self.limit,
        )
        query_params = params.model_dump(by_alias=True, exclude_none=True)
        response = self.client.get("/api/v1/402/discovery/search", params=query_params)
        search_response = DiscoverySearchResponse(**response)

        documents = []
        for agent in search_response.agents:
            # Build document content from agent data
            content_parts = []
            if agent.name:
                content_parts.append(f"Agent: {agent.name}")
            if agent.description:
                content_parts.append(f"Description: {agent.description}")
            if agent.trust_score is not None:
                content_parts.append(f"Trust Score: {agent.trust_score}")
            if agent.service_types:
                content_parts.append(f"Service Types: {', '.join(agent.service_types)}")
            if agent.capabilities:
                content_parts.append(f"Capabilities: {agent.capabilities}")

            metadata: dict[str, Any] = {
                "agent_id": agent.agent_id,
                "source": "ethys_discovery",
            }
            if agent.agent_id_key:
                metadata["agent_id_key"] = agent.agent_id_key
            if agent.trust_score is not None:
                metadata["trust_score"] = agent.trust_score
            if agent.service_types:
                metadata["service_types"] = agent.service_types

            documents.append(
                Document(
                    page_content="\n".join(content_parts),
                    metadata=metadata,
                )
            )

        return documents

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents asynchronously."""
        params = DiscoverySearchParams(
            query=query,
            min_trust_score=self.min_trust_score if self.min_trust_score > 0 else None,
            service_types=self.service_types if self.service_types else None,
            limit=self.limit,
        )
        query_params = params.model_dump(by_alias=True, exclude_none=True)
        response = await self.client.aget("/api/v1/402/discovery/search", params=query_params)
        search_response = DiscoverySearchResponse(**response)

        documents = []
        for agent in search_response.agents:
            content_parts = []
            if agent.name:
                content_parts.append(f"Agent: {agent.name}")
            if agent.description:
                content_parts.append(f"Description: {agent.description}")
            if agent.trust_score is not None:
                content_parts.append(f"Trust Score: {agent.trust_score}")
            if agent.service_types:
                content_parts.append(f"Service Types: {', '.join(agent.service_types)}")
            if agent.capabilities:
                content_parts.append(f"Capabilities: {agent.capabilities}")

            metadata: dict[str, Any] = {
                "agent_id": agent.agent_id,
                "source": "ethys_discovery",
            }
            if agent.agent_id_key:
                metadata["agent_id_key"] = agent.agent_id_key
            if agent.trust_score is not None:
                metadata["trust_score"] = agent.trust_score
            if agent.service_types:
                metadata["service_types"] = agent.service_types

            documents.append(
                Document(
                    page_content="\n".join(content_parts),
                    metadata=metadata,
                )
            )

        return documents

