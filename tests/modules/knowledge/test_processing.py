import pytest
from uuid import uuid4
from decisionos.modules.knowledge.processing import (
    FileProcessor,
    FileProcessingResult,
    compute_content_hash,
    get_file_mime_type,
    compute_file_hash,
    _normalize_text,
)


def test_compute_content_hash():
    """Test content hash computation."""
    hash1 = compute_content_hash("test content")
    hash2 = compute_content_hash("test content")
    hash3 = compute_content_hash("different content")

    assert hash1 == hash2  # Same content → same hash
    assert hash1 != hash3  # Different content → different hash


def test_get_file_mime_type():
    """Test MIME type detection."""
    pdf_content = b"%PDF-1.4 test"
    mime = get_file_mime_type(pdf_content)

    assert "pdf" in mime.lower()


def test_normalize_text():
    """Test text normalization."""
    # Multiple spaces → single space
    result = _normalize_text("  hello   world  ")
    assert result == "hello world"

    # Multiple newlines → max 2
    result = _normalize_text("hello\n\n\n\nworld")
    assert "\n\n" in result
    assert not result.startswith("\n\n\n")


def test_normalize_text_empty():
    """Test normalization of empty text."""
    result = _normalize_text("")
    assert result == ""


def test_normalize_text_single_line():
    """Test normalization of single line text."""
    result = _normalize_text("  hello  ")
    assert result == "hello"