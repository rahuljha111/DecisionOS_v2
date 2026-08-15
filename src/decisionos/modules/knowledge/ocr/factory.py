from __future__ import annotations

from decisionos.core.config.settings import get_settings
from decisionos.modules.knowledge.ocr.provider import OCRProvider
from decisionos.modules.knowledge.ocr.tesseract import TesseractOCRProvider


class OCRProviderFactory:
    """Factory for creating OCR providers based on configuration."""

    @staticmethod
    def create_provider() -> OCRProvider:
        """Create an OCR provider based on application settings.

        Returns:
            An instance of an OCRProvider implementation.

        Raises:
            ValueError: If the configured OCR provider is not supported.
        """
        settings = get_settings()
        provider_name = settings.ocr_provider.lower()

        if provider_name == "tesseract":
            return TesseractOCRProvider()
        # TODO: Add other providers like PaddleOCR, Baidu OCR, etc.
        else:
            raise ValueError(f"Unsupported OCR provider: {provider_name}")