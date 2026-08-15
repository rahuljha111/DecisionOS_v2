from __future__ import annotations

from typing import List, Optional, Dict, Any, Set

from decisionos.modules.rag.schemas import RagSearchResult


class ContextBuilder:
    """Builds bounded context from retrieved RAG chunks.

    Responsibilities:
    - Accept retrieved chunks
    - Remove duplicate content/chunks
    - Preserve source metadata
    - Order chunks deterministically
    - Enforce a configurable token/context budget
    - Return bounded context

    Design: provider-independent token counting abstraction
    so the tokenizer can later become provider/model-specific.
    """

    def __init__(self, max_tokens: int = 4000, tokenizer_name: str | None = None) -> None:
        self.max_tokens = max_tokens
        self.tokenizer_name = tokenizer_name
        # Simple character-to-token ratio as a fallback
        self._char_per_token_ratio = 3.5  # rough estimate

    def dedup(self, chunks: List[RagSearchResult]) -> list[RagSearchResult]:
        """Remove duplicate chunks based on content hash.

        Two chunks are considered duplicates if their content is identical
        after normalizing whitespace.

        Returns a list with duplicates removed, preserving first occurrence.
        """
        seen: set[str] = set()
        result: list[RagSearchResult] = []

        for chunk in chunks:
            # Normalize content for deduplication
            normalized = " ".join(chunk.content.split())
            content_hash = hash(normalized)

            if content_hash in seen:
                continue  # Skip duplicate

            seen.add(content_hash)
            result.append(chunk)

        return result

    def order(self, chunks: list[RagSearchResult]) -> list[RagSearchResult]:
        """Order chunks deterministically.

        Currently orders by similarity score descending (highest first).
        This can be overridden by subclasses or config for different
        ranking strategies (e.g., recency, importance, etc.).
        """
        return sorted(chunks, key=lambda c: c.similarity_score, reverse=True)

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text string.

        Uses a simple character-to-token ratio as a fallback.
        Subclasses should override with provider/model-specific tokenization.

        Args:
            text: The text to estimate tokens for

        Returns:
            Estimated token count
        """
        if not text:
            return 0
        # Rough estimate: divide by typical ratio
        return max(1, int(len(text) / self._char_per_token_ratio))

    def enforce_budget(
        self, chunks: list[RagSearchResult]
    ) -> tuple[list[RagSearchResult], int]:
        """Enforce a token budget on the chunk list.

        Iteratively adds chunks until the budget is exceeded,
        then returns the bounded list.

        Returns:
            Tuple of (bounded_chunks, total_estimated_tokens)
        """
        bounded: list[RagSearchResult] = []
        total_tokens = 0

        for chunk in chunks:
            chunk_tokens = self.estimate_tokens(chunk.content)
            if total_tokens + chunk_tokens > self.max_tokens:
                # Don't add this chunk; we've hit the budget
                break
            bounded.append(chunk)
            total_tokens += chunk_tokens

        return bounded, total_tokens

    def build_context(self, chunks: list[RagSearchResult]) -> dict[str, Any]:
        """Build a context dictionary from chunks.

        Each chunk's content is included with its source metadata.
        Returns a structure suitable for prompt injection.

        Returns:
            Dict with 'chunks' list and 'total_tokens' estimate
        """
        ordered = self.order(chunks)
        bounded, total_tokens = self.enforce_budget(ordered)

        chunk_texts: list[dict[str, Any]] = []
        for i, chunk in enumerate(bounded, start=1):
            chunk_texts.append(
                {
                    "chunk_index": i,
                    "content": chunk.content,
                    "source_type": chunk.source_type,
                    "document_id": str(chunk.document_id),
                    "chunk_id": str(chunk.chunk_id),
                    "similarity_score": chunk.similarity_score,
                    "metadata": chunk.metadata,
                }
            )

        return {
            "chunks": chunk_texts,
            "total_estimated_tokens": total_tokens,
            "max_tokens_budget": self.max_tokens,
            "chunk_count": len(bounded),
        }

    def build(
        self,
        chunks: list[RagSearchResult],
    ) -> tuple[list[RagSearchResult], dict[str, Any]]:
        """Full context building pipeline.

        1. Deduplicate
        2. Order deterministically
        3. Enforce token budget
        4. Build context dict

        Returns:
            Tuple of (selected_chunks, context_dict)
        """
        deduped = self.dedup(chunks)
        ordered = self.order(deduped)
        bounded, total_tokens = self.enforce_budget(ordered)
        # Use the bounded (deduped + budget-filtered) chunks for context building
        context_dict = self.build_context(bounded)

        return bounded, context_dict