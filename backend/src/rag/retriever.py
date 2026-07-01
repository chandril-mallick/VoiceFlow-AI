"""
VoiceFlow AI — Qdrant Retriever
Tenant-isolated vector search with hybrid retrieval and source attribution.
"""

import logging
from typing import Optional

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.core.config import settings
from src.rag.embeddings import get_embedding_function

logger = logging.getLogger(__name__)

_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """Get or create the Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        logger.info("✅ Connected to Qdrant at %s:%s", settings.qdrant_host, settings.qdrant_port)
    return _qdrant_client


def get_qdrant_store(
    collection_name: str,
    embeddings=None,
) -> QdrantVectorStore:
    """Get a QdrantVectorStore for a specific tenant collection."""
    if embeddings is None:
        embeddings = get_embedding_function()

    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=collection_name,
        embedding=embeddings,
    )


async def search_knowledge(
    query: str,
    tenant_id: str,
    collection_name: Optional[str] = None,
    top_k: int = 5,
    score_threshold: float = 0.3,
) -> list[dict]:
    """
    Search the knowledge base for a tenant.

    Args:
        query: Search query text.
        tenant_id: Tenant ID for isolation.
        collection_name: Qdrant collection name (defaults to tenant_{tenant_id}).
        top_k: Number of results to return.
        score_threshold: Minimum similarity score.

    Returns:
        List of dicts with: content, source, score, metadata
    """
    if not collection_name:
        collection_name = f"tenant_{tenant_id}"

    try:
        store = get_qdrant_store(collection_name)
        results = await store.asimilarity_search_with_score(query, k=top_k)

        documents = []
        for doc, score in results:
            if score >= score_threshold:
                documents.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "score": round(score, 3),
                    "metadata": doc.metadata,
                })

        logger.info(
            "Knowledge search: %d results for '%s...' (tenant=%s)",
            len(documents), query[:50], tenant_id,
        )
        return documents

    except Exception as e:
        logger.error("Knowledge search failed: %s", e)
        return []


async def build_rag_context(
    query: str,
    tenant_id: str,
    max_context_length: int = 2000,
) -> str:
    """
    Build a context string from RAG results for the LLM.
    Assembles top results into a formatted context block.
    """
    results = await search_knowledge(query, tenant_id)

    if not results:
        return ""

    context_parts = ["Based on our company knowledge base:\n"]
    current_length = 0

    for r in results:
        entry = f"\n[Source: {r['source']}]\n{r['content']}\n"
        if current_length + len(entry) > max_context_length:
            break
        context_parts.append(entry)
        current_length += len(entry)

    return "".join(context_parts)


async def delete_tenant_collection(tenant_id: str) -> bool:
    """Delete a tenant's entire vector collection."""
    collection_name = f"tenant_{tenant_id}"
    try:
        client = get_qdrant_client()
        client.delete_collection(collection_name)
        logger.info("🗑️ Deleted collection: %s", collection_name)
        return True
    except Exception as e:
        logger.error("Failed to delete collection %s: %s", collection_name, e)
        return False
