from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RagSearchRequest(BaseModel):
    """Request model for RAG semantic search."""

    query: str = Field(..., min_length=1, description="The search query text")
    top_k: int = Field(
        default=10, ge=1, le=100, description="Maximum number of results to return"
    )
    score_threshold: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Minimum similarity score threshold (0-1 for cosine)"
    )

    # Optional filters
    document_ids: Optional[List[UUID]] = Field(
        default=None, description="Optional: filter by specific document IDs"
    )
    source_types: Optional[List[str]] = Field(
        default=None, description="Optional: filter by source types (e.g., 'document', 'web')"
    )
    metadata_filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional: additional metadata filters"
    )

    @validator("query")
    def query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Query must not be empty")
        return v.strip()


class RagSearchResult(BaseModel):
    """Result model for a single RAG search hit."""

    chunk_id: UUID
    document_id: UUID
    content: str
    similarity_score: float
    chunk_index: int = Field(default=0, ge=0)
    source_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class RagSearchResponse(BaseModel):
    """Response model for RAG search endpoint."""

    results: List[RagSearchResult]
    total: int
    query: str
    top_k: int
    score_threshold: float

    model_config = {"from_attributes": True}