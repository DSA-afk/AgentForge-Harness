import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.config.config import settings

_tokenize = AutoTokenizer.from_pretrained(settings.RERANKER_MODEL_PATH)
_model = AutoModelForSequenceClassification.from_pretrained(settings.RERANKER_MODEL_PATH).eval()


def rerank(query: str, candidates: list, top_k: int = 5):
    texts = [c.payload["text"] for c in candidates]

    inputs = _tokenize(
        [query] * len(texts), texts,
        padding=True, truncation=True,
        max_length=512, return_tensors="pt"
    )
    with torch.no_grad():
        logits = _model(**inputs).logits.view(-1).float()

    scores = torch.sigmoid(logits).tolist()
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)

    return [
        {"score": s, "text": c.payload["text"], "payload": c.payload}
        for s, c in ranked[:top_k]
    ]
