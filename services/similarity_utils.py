import re
import threading
from sklearn.metrics.pairwise import cosine_similarity as cosine_sim

_sbert_model = None
_sbert_en_model = None
_sbert_lock = threading.Lock()
_sbert_en_lock = threading.Lock()


def get_sbert():
    global _sbert_model
    if _sbert_model is None:
        with _sbert_lock:
            if _sbert_model is None:
                from sentence_transformers import SentenceTransformer
                _sbert_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _sbert_model


def get_sbert_en():
    global _sbert_en_model
    if _sbert_en_model is None:
        with _sbert_en_lock:
            if _sbert_en_model is None:
                from sentence_transformers import SentenceTransformer
                _sbert_en_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _sbert_en_model


def is_thai(text: str) -> bool:
    return bool(re.search(r'[฀-๿]', text or ''))


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute SBERT cosine similarity between two texts. Returns 0.0–1.0."""
    if not text1 or not text2:
        return 0.0
    model = get_sbert() if is_thai(text1) else get_sbert_en()
    embs = model.encode([text1, text2], show_progress_bar=False)
    sim = float(cosine_sim([embs[0]], [embs[1]])[0][0])
    return round(max(0.0, min(1.0, sim)), 4)
