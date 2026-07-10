from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import load_app_config
from src.models import Citation


class LeaseIndex:
    """Lightweight TF-IDF index over lease clauses — no external vector DB required."""

    def __init__(self, clauses: list[dict]):
        self._clauses = clauses
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        corpus = [f"{c['title']} {c['text']}" for c in clauses]
        self._matrix = self._vectorizer.fit_transform(corpus) if corpus else None

    def search(self, query: str, lease_id: str | None = None, top_k: int | None = None) -> list[Citation]:
        if not self._clauses or self._matrix is None:
            return []

        cfg = load_app_config().get("retrieval", {})
        top_k = top_k or cfg.get("top_k", 3)
        min_score = cfg.get("min_score", 0.08)

        candidates = [
            (i, c) for i, c in enumerate(self._clauses) if lease_id is None or c["lease_id"] == lease_id
        ]
        if not candidates:
            return []

        indices = [i for i, _ in candidates]
        q_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self._matrix[indices]).flatten()

        ranked = sorted(zip(indices, scores), key=lambda x: x[1], reverse=True)
        out: list[Citation] = []
        for idx, score in ranked[:top_k]:
            if score < min_score:
                continue
            c = self._clauses[idx]
            out.append(
                Citation(
                    lease_id=c["lease_id"],
                    section=c["section"],
                    title=c["title"],
                    excerpt=c["text"][:280],
                    score=round(float(score), 4),
                )
            )
        return out
