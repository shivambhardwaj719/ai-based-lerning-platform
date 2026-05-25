"""
RAG Knowledge Retriever using Qdrant vector database.
Supports semantic search across documentation, editorials, and study materials.
"""
from __future__ import annotations

from typing import Any

import structlog
from langchain_openai import OpenAIEmbeddings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, SearchRequest, VectorParams

from core.config import settings

log = structlog.get_logger()

COLLECTION_NAME = "knowledge_base"
EMBEDDING_DIM = 1536


class KnowledgeRetriever:
    def __init__(self) -> None:
        self._client: AsyncQdrantClient | None = None
        self.embeddings = OpenAIEmbeddings(
            model=settings.DEFAULT_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

    async def _get_client(self) -> AsyncQdrantClient:
        if not self._client:
            self._client = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY or None,
            )
            # Ensure collection exists
            collections = await self._client.get_collections()
            names = [c.name for c in collections.collections]
            if COLLECTION_NAME not in names:
                await self._client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
                )
        return self._client

    async def retrieve(
        self,
        query: str,
        k: int = 5,
        filter_: dict | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve top-k relevant documents for a query."""
        client = await self._get_client()
        query_vector = await self.embeddings.aembed_query(query)

        results = await client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=k,
            with_payload=True,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "content": hit.payload.get("content", ""),
                "title": hit.payload.get("title", ""),
                "source": hit.payload.get("source", ""),
                "metadata": hit.payload,
            }
            for hit in results
        ]

    async def index_document(
        self,
        doc_id: str,
        content: str,
        title: str,
        source: str = "knowledge_base",
        metadata: dict | None = None,
    ) -> None:
        """Index a document into the vector store."""
        client = await self._get_client()
        vector = await self.embeddings.aembed_documents([content])

        point = PointStruct(
            id=hash(doc_id) % (2**63),  # Qdrant requires int IDs
            vector=vector[0],
            payload={
                "doc_id": doc_id,
                "content": content,
                "title": title,
                "source": source,
                **(metadata or {}),
            },
        )
        await client.upsert(collection_name=COLLECTION_NAME, points=[point])

    async def bulk_index(self, documents: list[dict]) -> None:
        """Bulk index documents efficiently."""
        client = await self._get_client()
        texts = [d["content"] for d in documents]
        vectors = await self.embeddings.aembed_documents(texts)

        points = [
            PointStruct(
                id=hash(doc["doc_id"]) % (2**63),
                vector=vec,
                payload={k: v for k, v in doc.items() if k != "doc_id"},
            )
            for doc, vec in zip(documents, vectors, strict=False)
        ]
        await client.upsert(collection_name=COLLECTION_NAME, points=points)
        log.info("Bulk indexed documents", count=len(points))
