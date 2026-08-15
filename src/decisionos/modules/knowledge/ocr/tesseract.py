from __future__ import annotations

import logging
from typing import Optional
from PIL import Image

from decisionos.modules.knowledge.ocr.provider import OCRProvider, OCRProviderError
from decisionos.core.config.settings import get_settings

logger = logging.getLogger(__name__)


class TesseractOCRProvider(OCRProvider):
    """OCR provider using Tesseract OCR."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.tesseract_cmd = self.settings.ocr_tesseract_cmd
        self.languages = self.settings.ocr_languages

        # If tesseract_cmd is set, we need to configure pytesseract
        if self.tesseract_cmd:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            except ImportError:
                logger.warning("pytesseract not installed, Tesseract OCR will not be available")
                raise OCRProviderError("pytesseract is not installed")
        else:
            # Use default path
            try:
                import pytesseract
                # Check if tesseract is available
                pytesseract.get_tesseract_version()
            except ImportError:
                logger.warning("pytesseract not installed, Tesseract OCR will not be available")
                raise OCRProviderError("pytesseract is not installed")
            except Exception as e:
                logger.warning(f"Tesseract not available: {e}")
                raise OCRProviderError(f"Tesseract is not available: {e}")

    async def extract_text(self, image: Image.Image) -> str:
        """Extract text from an image using Tesseract OCR."""
        try:
            import pytesseract
            # Run OCR
            text = pytesseract.image_to_string(image, lang=self.languages)
            return text
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            raise OCRProviderError(f"Tesseract OCR failed: {e}")

    async def health_check(self) -> bool:
        """Check if Tesseract OCR is healthy."""
        try:
            import pytesseract
            # Try to get version
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False