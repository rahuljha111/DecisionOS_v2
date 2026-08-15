from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image


class OCRProvider(ABC):
    """Abstract base class for OCR providers.

    All OCR provider implementations must adhere to this interface so that
    the FileProcessor remains OCR-provider agnostic.
    """

    @abstractmethod
    async def extract_text(self, image: Image.Image) -> str:
        """Extract text from an image.

        Args:
            image: A PIL Image object.

        Returns:
            The extracted text as a string.

        Raises:
            OCRProviderError: If OCR extraction fails.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the OCR provider is healthy and reachable.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        pass


class OCRProviderError(Exception):
    """Raised when an OCR provider fails."""
    pass