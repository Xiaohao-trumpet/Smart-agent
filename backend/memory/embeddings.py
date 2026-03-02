"""Embedding provider with remote OpenAI-compatible support and local fallback."""

from __future__ import annotations

import hashlib
import math
import re
from typing import List, Optional

from ..utils.httpx_compat import patch_httpx_for_openai

patch_httpx_for_openai()
from openai import OpenAI


class EmbeddingProvider:
    """Embeddings client with deterministic local fallback."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        embedding_model: str,
        dimension: int = 256,
        use_remote: bool = True,
    ):
        self.embedding_model = embedding_model
        self.dimension = max(32, dimension)
        self.use_remote = use_remote
        self._client: Optional[OpenAI] = None

        if self.use_remote:
            self._client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                max_retries=0,
                timeout=10.0,
            )

    def _normalize(self, vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(v * v for v in vector))
        if norm == 0:
            return vector
        return [v / norm for v in vector]

    def _fallback_embedding(self, text: str) -> List[float]:
        # Token hashing vectorizer: stable, local, no external dependency.
        vec = [0.0] * self.dimension
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        if not tokens:
            return vec
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % self.dimension
            vec[idx] += 1.0
        return self._normalize(vec)

    def embed_text(self, text: str) -> List[float]:
        if not self.use_remote or self._client is None:
            return self._fallback_embedding(text)

        try:
            result = self._client.embeddings.create(
                model=self.embedding_model,
                input=[text],
            )
            vector = list(result.data[0].embedding)
            if len(vector) == self.dimension:
                return self._normalize(vector)
            if len(vector) > self.dimension:
                return self._normalize(vector[: self.dimension])
            padded = vector + [0.0] * (self.dimension - len(vector))
            return self._normalize(padded)
        except Exception:
            return self._fallback_embedding(text)
