from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np

from decisionos.core.exceptions import AppError


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    All provider implementations must adhere to this interface so that
    business logic remains provider-agnostic (AI Provider Independence rule).
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the embedding model."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Dimensionality of the embedding vectors."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats representing the embedding vector.

        Raises:
            ServiceError: If embedding generation fails.
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of texts.

        Args:
            texts: A list of input texts to embed.

        Returns:
            A list of embedding vectors, one per input text.

        Raises:
            ServiceError: If embedding generation fails.
        """
        pass

    async def health_check(self) -> bool:
        """Check if the provider is healthy and reachable.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        try:
            await self.embed("")
            return True
        except Exception:
            return False


class ProviderError(AppError):
    """Raised when an embedding provider fails."""

    def __init__(self, message: str, provider: str | None = None) -> None:
        super().__init__(f"Embedding provider error: {message}")
        self.provider = provider


def get_embedding_provider() -> EmbeddingProvider:
    """Composition boundary for embedding providers.

    Returns the configured :class:`EmbeddingProvider` based on application
    settings. The concrete implementation (and any provider-selection logic)
    stays behind this boundary so callers depend only on the abstract
    interface, never on a specific provider class.

    Dependency flow:

        Router / task / service
              ↓
        get_embedding_provider()  -> EmbeddingProvider
              ↓
        concrete provider (e.g. HuggingFaceEmbeddingProvider)
    """
    from decisionos.core.config.settings import get_settings

    settings = get_settings()
    provider_name = settings.embedding_provider

    if provider_name == "huggingface":
        # Imported lazily so the heavy sentence-transformers dependency is only
        # loaded when the HF provider is actually selected.
        from decisionos.modules.knowledge.providers.hf_embedding import (
            HuggingFaceEmbeddingProvider,
        )

        return HuggingFaceEmbeddingProvider(
            model_name=settings.embedding_model_name,
            dimensions=settings.embedding_dimensions,
        )

    raise ProviderError(
        f"Unknown embedding provider: {provider_name!r}",
        provider=provider_name,
    )