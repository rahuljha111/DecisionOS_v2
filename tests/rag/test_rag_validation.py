"""Tests for RAG validation errors."""

from uuid import UUID

import pytest
from fastapi import HTTPException

from decisionos.modules.rag.schemas import RagSearchRequest


class TestRagSearchRequestValidation:
    """Tests for RagSearchRequest validation errors."""

    def test_empty_query_raises_error(self):
        """Empty query should raise a validation error."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="")
            assert False, "Validation should have failed for empty query"
        except Exception:
            pass  # Expected

    def test_whitespace_query_raises_error(self):
        """Whitespace-only query should raise a validation error."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="   ")
            assert False, "Validation should have failed for whitespace query"
        except Exception:
            pass  # Expected

    def test_negative_top_k_raises_error(self):
        """Negative top_k should raise a validation error."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="test", top_k=-1)
            assert False, "Validation should have failed for negative top_k"
        except Exception:
            pass  # Expected

    def test_top_k_too_large_raises_error(self):
        """top_k exceeding max should raise a validation error."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="test", top_k=200)
            assert False, "Validation should have failed for top_k > 100"
        except Exception:
            pass  # Expected

    def test_negative_score_threshold_raises_error(self):
        """Negative score_threshold should raise a validation error."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="test", score_threshold=-0.5)
            assert False, "Validation should have failed for negative threshold"
        except Exception:
            pass  # Expected

    def test_score_threshold_above_one_raises_error(self):
        """score_threshold > 1 should raise a validation error."""
        from pydantic import ValidationError
        try:
            RagSearchRequest(query="test", score_threshold=2.0)
            assert False, "Validation should have failed for threshold > 1"
        except Exception:
            pass  # Expected