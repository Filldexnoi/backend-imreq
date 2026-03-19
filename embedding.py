# embedding.py
from sentence_transformers import SentenceTransformer

# โหลด model ครั้งเดียว (สำคัญมาก)
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

def embed(text: str) -> list[float]:
    """
    Convert text to embedding vector (768 dimensions)
    """
    embedding = model.encode(
        text,
        normalize_embeddings=True  # แนะนำ เปิด
    )
    return embedding.tolist()
