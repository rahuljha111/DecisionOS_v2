from __future__ import annotations

import asyncio
from functools import partial
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from decisionos.modules.knowledge.embedding import EmbeddingProvider, ProviderError


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Concrete embedding provider using HuggingFace sentence-transformers.

    This provider uses local sentence-transformers models to generate
    embeddings. The model is loaded once and cached for the lifetime
    of the application.

    Configuration comes from the application settings:
    - embedding_model_name: The model identifier
    - embedding_dimensions: The expected dimensionality of embeddings.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dimensions: int = 384,
    ) -> None:
        self._model_name = model_name
        self._dimensions = dimensions
        self._model: SentenceTransformer | None = None
        self._lock = asyncio.Lock()

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def _ensure_model_loaded(self) -> SentenceTransformer:
        """Lazily load the model once in a thread pool."""
        if self._model is None:
            async with self._lock:
                if self._model is None:
                    loop = asyncio.get_running_loop()
                    self._model = await loop.run_in_executor(
                        None,
                        partial(
                            SentenceTransformer,
                            self._model_name,
                        ),
                    )

        return self._model

    async def embed(self, text: str) -> List[float]:
        """Generate an embedding for a single text."""
        if not text or not text.strip():
            raise ProviderError("Empty text provided for embedding")

        try:
            model = await self._ensure_model_loaded()
            loop = asyncio.get_running_loop()

            encode = partial(
                model.encode,
                text,
                convert_to_tensor=False,
            )

            embedding_vec = await loop.run_in_executor(None, encode)

            embedding_vec = np.asarray(embedding_vec, dtype=float)

            if embedding_vec.ndim == 1:
                embedding_vec = embedding_vec.tolist()
            elif embedding_vec.ndim == 2:
                embedding_vec = embedding_vec[0].tolist()
            else:
                raise ValueError(
                    f"Unexpected embedding dimensions: {embedding_vec.ndim}"
                )

            if len(embedding_vec) < self._dimensions:
                embedding_vec.extend(
                    [0.0] * (self._dimensions - len(embedding_vec))
                )
            elif len(embedding_vec) > self._dimensions:
                embedding_vec = embedding_vec[: self._dimensions]

            return embedding_vec

        except Exception as e:
            raise ProviderError(
                str(e),
                provider="huggingface",
            ) from e

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []

        try:
            model = await self._ensure_model_loaded()
            loop = asyncio.get_running_loop()

            encode = partial(
                model.encode,
                texts,
                convert_to_tensor=False,
            )

            embedding_matrix = await loop.run_in_executor(None, encode)

            embedding_matrix = np.asarray(
                embedding_matrix,
                dtype=float,
            )

            if embedding_matrix.ndim == 1:
                result = [embedding_matrix.tolist()]
            elif embedding_matrix.ndim == 2:
                result = [
                    row.tolist()
                    for row in embedding_matrix
                ]
            else:
                raise ValueError(
                    f"Unexpected embedding dimensions: "
                    f"{embedding_matrix.ndim}"
                )

            result = [
                (
                    vec
                    + [0.0] * (self._dimensions - len(vec))
                )[: self._dimensions]
                for vec in result
            ]

            return result

        except Exception as e:
            raise ProviderError(
                str(e),
                provider="huggingface",
            ) from e

    async def health_check(self) -> bool:
        """Check provider health by generating a small embedding."""
        try:
            await self.embed("health check")
            return True
        except Exception:
            return False