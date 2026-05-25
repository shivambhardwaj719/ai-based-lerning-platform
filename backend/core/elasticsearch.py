"""
Elasticsearch client manager for full-text search, problem search, and user search.
"""
from __future__ import annotations

from typing import Any

import structlog
from elasticsearch import AsyncElasticsearch, NotFoundError

from core.config import settings

log = structlog.get_logger()


class ElasticsearchManager:
    """Manages Elasticsearch connections and provides search helpers."""

    def __init__(self) -> None:
        self._client: AsyncElasticsearch | None = None

    async def connect(self) -> None:
        kwargs: dict = {
            "hosts": [settings.ELASTICSEARCH_URL],
            "retry_on_timeout": True,
            "max_retries": 3,
            "timeout": 30,
        }
        if settings.ELASTICSEARCH_PASSWORD:
            kwargs["http_auth"] = (settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)
        self._client = AsyncElasticsearch(**kwargs)
        info = await self._client.info()
        log.info("Elasticsearch connected", version=info["version"]["number"])

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
        log.info("Elasticsearch disconnected")

    async def health_check(self) -> bool:
        try:
            await self._client.ping()
            return True
        except Exception:
            return False

    @property
    def client(self) -> AsyncElasticsearch:
        if not self._client:
            msg = "Elasticsearch not connected"
            raise RuntimeError(msg)
        return self._client

    def _index(self, name: str) -> str:
        return f"{settings.ELASTICSEARCH_INDEX_PREFIX}_{name}"

    # ── Index management ──────────────────────────────────────────────────────

    async def create_index(self, name: str, mappings: dict, settings_: dict | None = None) -> None:
        index = self._index(name)
        if not await self.client.indices.exists(index=index):
            body: dict = {"mappings": mappings}
            if settings_:
                body["settings"] = settings_
            await self.client.indices.create(index=index, body=body)
            log.info("Elasticsearch index created", index=index)

    async def delete_index(self, name: str) -> None:
        await self.client.indices.delete(index=self._index(name), ignore_unavailable=True)

    # ── Document operations ───────────────────────────────────────────────────

    async def index_document(self, index: str, doc_id: str, document: dict) -> None:
        await self.client.index(index=self._index(index), id=doc_id, document=document)

    async def update_document(self, index: str, doc_id: str, partial: dict) -> None:
        await self.client.update(index=self._index(index), id=doc_id, body={"doc": partial})

    async def delete_document(self, index: str, doc_id: str) -> None:
        try:
            await self.client.delete(index=self._index(index), id=doc_id)
        except NotFoundError:
            pass

    async def get_document(self, index: str, doc_id: str) -> dict | None:
        try:
            result = await self.client.get(index=self._index(index), id=doc_id)
            return result["_source"]
        except NotFoundError:
            return None

    # ── Search ────────────────────────────────────────────────────────────────

    async def search(
        self,
        index: str,
        query: dict,
        size: int = 10,
        from_: int = 0,
        sort: list | None = None,
        highlight: dict | None = None,
    ) -> dict:
        body: dict = {"query": query, "size": size, "from": from_}
        if sort:
            body["sort"] = sort
        if highlight:
            body["highlight"] = highlight
        return await self.client.search(index=self._index(index), body=body)

    async def multi_match_search(
        self,
        index: str,
        query_text: str,
        fields: list[str],
        size: int = 10,
        filters: list[dict] | None = None,
    ) -> list[dict]:
        must: list[dict] = [{"multi_match": {"query": query_text, "fields": fields, "type": "best_fields"}}]
        if filters:
            query = {"bool": {"must": must, "filter": filters}}
        else:
            query = {"bool": {"must": must}}
        result = await self.search(index, query, size=size)
        return [
            {"id": hit["_id"], "score": hit["_score"], **hit["_source"]}
            for hit in result["hits"]["hits"]
        ]

    async def bulk_index(self, index: str, documents: list[dict]) -> None:
        """Bulk index documents efficiently."""
        if not documents:
            return
        operations = []
        for doc in documents:
            doc_id = doc.pop("id", None)
            operations.append({"index": {"_index": self._index(index), "_id": doc_id}})
            operations.append(doc)
        await self.client.bulk(body=operations)

    # ── Prebuilt index schemas ────────────────────────────────────────────────

    async def setup_indices(self) -> None:
        """Create all required indices with proper mappings."""
        await self.create_index(
            "problems",
            mappings={
                "properties": {
                    "title": {"type": "text", "analyzer": "english"},
                    "description": {"type": "text", "analyzer": "english"},
                    "tags": {"type": "keyword"},
                    "difficulty": {"type": "keyword"},
                    "acceptance_rate": {"type": "float"},
                    "created_at": {"type": "date"},
                }
            },
        )
        await self.create_index(
            "users",
            mappings={
                "properties": {
                    "username": {"type": "keyword"},
                    "full_name": {"type": "text"},
                    "bio": {"type": "text"},
                    "skills": {"type": "keyword"},
                }
            },
        )
        await self.create_index(
            "courses",
            mappings={
                "properties": {
                    "title": {"type": "text", "analyzer": "english"},
                    "description": {"type": "text", "analyzer": "english"},
                    "tags": {"type": "keyword"},
                    "level": {"type": "keyword"},
                }
            },
        )


es_manager = ElasticsearchManager()
