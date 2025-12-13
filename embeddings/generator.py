import numpy as np
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed(text: str) -> np.ndarray:
    vec = _model.encode(text, convert_to_numpy=True)
    return vec.astype(np.float32)
