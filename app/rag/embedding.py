from FlagEmbedding import BGEM3FlagModel
from app.config.config import settings

_model = BGEM3FlagModel(settings.EMBEDDING_MODEL_PATH, use_fp16=False)


def embed_texts(texts: list[str]) -> list[dict]:

    out = _model.encode(texts, return_dense=True, return_sparse=True)
    result = []
    for i in range(len(texts)):
        dense = out['dense_vecs'][i].tolist()
        lw = out['lexical_weights'][i]
        sparse = {
            "indices": [int(k) for k in lw],
            "values": [float(v) for v in lw.values()]
        }
        result.append({"dense": dense, "sparse": sparse})

    return result
