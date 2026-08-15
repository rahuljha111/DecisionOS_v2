import pytest
from unittest.mock import Mock, patch
from decisionos.modules.knowledge.providers.hf_embedding import (
    HuggingFaceEmbeddingProvider,
    ProviderError,
)


def test_hf_embedding_provider_initialization():
    """Test provider initialization with default params."""
    provider = HuggingFaceEmbeddingProvider()
    assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    assert provider.dimensions == 384


def test_hf_embedding_provider_custom():
    """Test provider initialization with custom params."""
    provider = HuggingFaceEmbeddingProvider(
        model_name="custom-model", dimensions=256
    )
    assert provider.model_name == "custom-model"
    assert provider.dimensions == 256


async def test_hf_embedding_embed():
    """Test embedding generation."""
    provider = HuggingFaceEmbeddingProvider()

    with patch.object(provider, "_ensure_model_loaded") as mock_load:
        mock_model = Mock()
        mock_model.encode.return_value = [0.1] * 384
        mock_load.return_value = mock_model

        result = await provider.embed("test text")
        assert len(result) == 384
        assert all(isinstance(v, float) for v in result)


async def test_hf_embedding_embed_empty():
    """Test embedding with empty text raises error."""
    provider = HuggingFaceEmbeddingProvider()

    with pytest.raises(ProviderError):
        await provider.embed("")


async def test_hf_embedding_embed_batch():
    """Test batch embedding generation."""
    provider = HuggingFaceEmbeddingProvider()

    with patch.object(provider, "_ensure_model_loaded") as mock_load:
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1] * 384] * 3
        mock_load.return_value = mock_model

        results = await provider.embed_batch(["text1", "text2", "text3"])
        assert len(results) == 3
        assert all(len(r) == 384 for r in results)


async def test_hf_embedding_health_check():
    """Test health check."""
    provider = HuggingFaceEmbeddingProvider()

    with patch.object(provider, "embed") as mock_embed:
        mock_embed.return_value = [0.1] * 384
        result = await provider.health_check()
        assert result is True