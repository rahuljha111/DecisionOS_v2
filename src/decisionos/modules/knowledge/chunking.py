from __future__ import annotations

from typing import List, Tuple


class ChunkingConfig:
    """Configuration for text chunking."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        if min_chunk_size < 0:
            raise ValueError("min_chunk_size cannot be negative")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    min_chunk_size: int | None = None,
) -> List[Tuple[int, str]]:
    """Chunk raw text into overlapping segments.

    Returns:
        A list of (chunk_index, chunk_text) tuples.
    """
    if not text or not text.strip():
        return []

    config = ChunkingConfig(
        chunk_size=chunk_size if chunk_size is not None else 1000,
        chunk_overlap=(
            chunk_overlap if chunk_overlap is not None else 200
        ),
        min_chunk_size=(
            min_chunk_size if min_chunk_size is not None else 100
        ),
    )

    words = text.split()

    if len(words) <= config.min_chunk_size:
        return [(0, text)]

    chunks: List[Tuple[int, str]] = []
    start = 0

    while start < len(words):
        end = start + config.chunk_size
        chunk_words = words[start:end]
        content = " ".join(chunk_words)

        if len(content.strip()) >= config.min_chunk_size:
            chunk_index = len(chunks)
            chunks.append((chunk_index, content))

        if end >= len(words):
            break

        start = end - config.chunk_overlap

    return [(index, content) for index, content in chunks]


def chunk_text_with_metadata(
    text: str,
    document_id: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    min_chunk_size: int | None = None,
    page_number: int | None = None,
    section_text: str | None = None,
) -> List[dict]:
    """Chunk text and enrich each chunk with metadata.

    Returns:
        A list of chunk dictionaries containing document_id,
        chunk_index, content, and optional page/section metadata.
    """
    chunks = chunk_text(
        text,
        chunk_size,
        chunk_overlap,
        min_chunk_size,
    )

    result: List[dict] = []

    for index, content in chunks:
        chunk_meta = {
            "document_id": document_id,
            "chunk_index": index,
            "content": content,
            "content_hash": None,
        }

        if page_number is not None:
            chunk_meta["page_number"] = page_number

        if section_text is not None:
            chunk_meta["section_text"] = section_text

        result.append(chunk_meta)

    return result