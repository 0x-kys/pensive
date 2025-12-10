import numpy as np
from sentence_transformers import SentenceTransformer
from torch._tensor import Tensor

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed(text: str) -> Tensor:
    return model.encode(text)
