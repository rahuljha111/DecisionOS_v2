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