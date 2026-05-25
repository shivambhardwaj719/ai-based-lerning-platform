"""Search API: full-text search across problems, users, courses."""
from __future__ import annotations

from fastapi import APIRouter, Query
from core.elasticsearch import es_manager

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def global_search(
    q: str = Query(min_length=1, max_length=200),
    types: list[str] | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
) -> dict:
    search_types = types or ["problems", "users", "courses"]
    results: dict = {}

    for search_type in search_types:
        if search_type == "problems":
            hits = await es_manager.multi_match_search(
                "problems", q, ["title^3", "description", "tags^2"],
                size=page_size,
            )
            results["problems"] = hits
        elif search_type == "users":
            hits = await es_manager.multi_match_search(
                "users", q, ["username^3", "full_name^2", "bio"],
                size=page_size,
            )
            results["users"] = hits
        elif search_type == "courses":
            hits = await es_manager.multi_match_search(
                "courses", q, ["title^3", "description", "tags^2"],
                size=page_size,
            )
            results["courses"] = hits

    return {"query": q, "results": results}


@router.get("/problems")
async def search_problems(
    q: str = Query(min_length=1),
    difficulty: str | None = None,
    tags: list[str] | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    filters = []
    if difficulty:
        filters.append({"term": {"difficulty": difficulty}})
    if tags:
        filters.append({"terms": {"tags": tags}})

    hits = await es_manager.multi_match_search(
        "problems", q, ["title^3", "description", "tags^2"],
        size=page_size, filters=filters,
    )
    return {"query": q, "hits": hits, "total": len(hits)}
