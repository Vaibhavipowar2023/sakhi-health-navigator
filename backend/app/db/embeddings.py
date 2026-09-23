"""Embedding utilities for semantic search.

Uses sentence-transformers to embed provider services and patient symptoms,
then cosine similarity to find the best matches.
"""

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    _EMBEDDINGS_AVAILABLE = True
except ImportError:
    np = None
    SentenceTransformer = None
    _EMBEDDINGS_AVAILABLE = False

_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def _get_model():
    if not _EMBEDDINGS_AVAILABLE:
        raise RuntimeError("sentence-transformers not installed")
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """Generate a 384-dim embedding vector for a text string."""
    model = _get_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch embed multiple texts at once (faster than one at a time)."""
    model = _get_model()
    vecs = model.encode(texts, normalize_embeddings=True)
    return vecs.tolist()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine similarity between two normalized vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b))


def find_similar(query_vec: list[float], documents: list[dict], top_k: int = 10) -> list[dict]:
    """Rank documents by cosine similarity to query_vec.

    Each document must have an 'embedding' field (list of floats).
    Returns top_k docs sorted by similarity score, with score added.
    """
    scored = []
    for doc in documents:
        if "embedding" not in doc or doc["embedding"] is None:
            continue
        score = cosine_similarity(query_vec, doc["embedding"])
        scored.append({**doc, "similarity_score": score})

    scored.sort(key=lambda d: d["similarity_score"], reverse=True)
    return scored[:top_k]
