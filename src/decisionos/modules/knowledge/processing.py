from __future__ import annotations

import hashlib
import os
from io import BytesIO
from typing import Optional,Dict, Any

import magic
import pdfplumber
from PIL import Image

from decisionos.core.exceptions import AppError
from decisionos.modules.knowledge.ocr import OCRProviderFactory


def compute_content_hash(content: str | bytes) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def get_file_mime_type(file_content: bytes) -> str:
    """Get the MIME type of file content."""
    return magic.from_buffer(file_content, mime=True)


def compute_file_hash(file_content: bytes) -> str:
    """Compute SHA-256 hash of raw file content."""
    return hashlib.sha256(file_content).hexdigest()


class FileProcessingResult:
    """Result of file processing operations."""

    def __init__(
        self,
        text: str,
        metadata: Dict[str, Any],
        content_hash: str,
        mime_type: str,
        pages: Optional[int] = None,
    ) -> None:
        self.text = text
        self.metadata = metadata
        self.content_hash = content_hash
        self.mime_type = mime_type
        self.pages = pages


class FileProcessor:
    """Handles extraction from various file formats."""

    SUPPORTED_MIME_TYPES = {
        "application/pdf": "pdf",
        "image/jpeg": "image",
        "image/png": "image",
        "image/tiff": "image",
        "image/gif": "image",
        "text/plain": "text",
        "text/markdown": "markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    async def process(self, file_content: bytes, filename: str) -> FileProcessingResult:
        """Process a file and extract text content.

        Args:
            file_content: Raw bytes of the file
            filename: Original filename

        Returns:
            FileProcessingResult with extracted text and metadata

        Raises:
            AppError: If processing fails or format is unsupported
        """
        mime_type = get_file_mime_type(file_content)
        file_type = self.SUPPORTED_MIME_TYPES.get(mime_type)

        if file_type is None:
            raise AppError(
                f"Unsupported file format: {mime_type}",
                status_code=400,
            )

        content_hash = compute_file_hash(file_content)

        try:
            if file_type == "pdf":
                return await self._process_pdf(file_content, content_hash)
            elif file_type == "image":
                return await self._process_image(file_content, content_hash, mime_type)
            elif file_type == "text":
                return await self._process_text(file_content, content_hash)
            elif file_type == "markdown":
                return await self._process_markdown(file_content, content_hash)
            elif file_type == "docx":
                return await self._process_docx(file_content, content_hash)
            else:
                raise AppError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise AppError(f"File processing failed: {e}")

    async def _process_pdf(self, file_content: bytes, content_hash: str) -> FileProcessingResult:
        """Extract text from PDF file."""
        text_parts = []
        metadata = {}
        pages = 0

        try:
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                pages = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    # Extract metadata if available
                    if not metadata and page.metadata:
                        metadata = dict(page.metadata)
        except Exception as e:
            raise AppError(f"PDF processing failed: {e}")

        full_text = "\n".join(text_parts) if text_parts else ""
        text = _normalize_text(full_text)

        meta = {
            "file_type": "pdf",
            "pages": pages,
            "content_hash": content_hash,
        }
        meta.update(metadata)

        return FileProcessingResult(text=text, metadata=meta, content_hash=content_hash,
                                    mime_type="application/pdf", pages=pages)

    async def _process_image(
        self, file_content: bytes, content_hash: str, mime_type: str
    ) -> FileProcessingResult:
        """Extract text from image using OCR."""
        try:
            image = Image.open(BytesIO(file_content))
        except Exception as e:
            raise AppError(f"Image opening failed: {e}")

        # Use OCR provider abstraction
        try:
            ocr_provider = OCRProviderFactory.create_provider()
            ocr_text = await ocr_provider.extract_text(image)
            text = _normalize_text(ocr_text.strip())
        except Exception as e:
            # Fallback: treat as empty if OCR fails
            text = ""

        # If OCR produces very little text, try to use image as-is
        if not text.strip():
            text = ""

        meta = {
            "file_type": "image",
            "mime_type": mime_type,
            "content_hash": content_hash,
            "ocr_used": bool(text.strip()),
        }

        return FileProcessingResult(
            text=text, metadata=meta, content_hash=content_hash,
            mime_type=mime_type, pages=None
        )

    async def _process_text(self, file_content: bytes, content_hash: str) -> FileProcessingResult:
        """Extract text from plain text file."""
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_content.decode("latin-1")
            except Exception:
                text = ""

        text = _normalize_text(text)

        return FileProcessingResult(
            text=text, metadata={"file_type": "text", "content_hash": content_hash},
            content_hash=content_hash, mime_type="text/plain"
        )

    async def _process_markdown(self, file_content: bytes, content_hash: str) -> FileProcessingResult:
        """Extract text from markdown file."""
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text = ""

        text = _normalize_text(text)

        return FileProcessingResult(
            text=text, metadata={"file_type": "markdown", "content_hash": content_hash},
            content_hash=content_hash, mime_type="text/markdown"
        )

    async def _process_docx(self, file_content: bytes, content_hash: str) -> FileProcessingResult:
        """Extract text from DOCX file."""
        try:
            import docx
            doc = docx.Document(BytesIO(file_content))
            text_parts = [para.text for para in doc.paragraphs if para.text]
            text = "\n".join(text_parts)
        except Exception as e:
            raise AppError(f"DOCX processing failed: {e}")

        text = _normalize_text(text)

        return FileProcessingResult(
            text=text, metadata={"file_type": "docx", "content_hash": content_hash},
            content_hash=content_hash, mime_type=
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


    def _normalize_text(text: str) -> str:
        """Normalize extracted text.

        - Strip leading/trailing whitespace
        - Collapse multiple whitespace lines
        - Remove excessive blank lines
        - Ensure consistent line endings
        """
        if not text:
            return ""

        # Collapse multiple spaces into single space
        text = " ".join(text.split())

        # Collapse multiple newlines into max 2
        import re
        text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

        return text.strip()
def _normalize_text(text: str) -> str:
    """Normalize extracted text."""
    if not text:
        return ""

    import re

    # Normalize line endings first.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse runs of spaces/tabs without destroying newlines.
    text = re.sub(r"[^\S\n]+", " ", text)

    # Collapse more than two consecutive newlines.
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()