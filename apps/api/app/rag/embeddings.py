import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class FastEmbedModel:
    """
    Local 384-dimensional dense semantic embedding generator using FastEmbed.
    Runs on CPU via ONNX Runtime with zero API key requirement ($0.00 cost).
    Includes graceful degradation to lexical search if model initialization fails.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension = 384
        self._model = None
        self._is_available = False
        self._init_attempted = False

    def initialize(self) -> bool:
        """Attempts to load the FastEmbed TextEmbedding ONNX model."""
        if self._init_attempted:
            return self._is_available

        self._init_attempted = True
        try:
            from fastembed import TextEmbedding
            # Initialize with default local cache
            self._model = TextEmbedding(model_name=self.model_name)
            self._is_available = True
            logger.info("fastembed_model_initialized", extra={"model": self.model_name, "dim": self.dimension})
            return True
        except Exception as e:
            logger.warning(
                "fastembed_init_failed_falling_back_to_lexical",
                extra={"error": str(e), "action": "lexical_fallback_enabled"}
            )
            self._is_available = False
            self._model = None
            return False

    @property
    def is_available(self) -> bool:
        if not self._init_attempted:
            self.initialize()
        return self._is_available

    def embed_documents(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generates 384-dimensional embeddings for a batch of documents."""
        if not self.is_available or self._model is None:
            return None

        try:
            embeddings_generator = self._model.embed(texts)
            embeddings = [list(vec) for vec in embeddings_generator]
            return embeddings
        except Exception as e:
            logger.error("fastembed_document_embedding_error", extra={"error": str(e)})
            return None

    def embed_query(self, text: str) -> Optional[List[float]]:
        """Generates a 384-dimensional embedding for a single search query."""
        if not self.is_available or self._model is None:
            return None

        try:
            embeddings_generator = self._model.embed([text])
            vector = list(next(embeddings_generator))
            return vector
        except Exception as e:
            logger.error("fastembed_query_embedding_error", extra={"error": str(e)})
            return None


# Global singleton instance
embedder = FastEmbedModel()
