from app.rag.loader import parse
from app.rag.embedding import embed_texts
from app.rag.loader import chunk_text
from app.rag.qdrant_store import qdrant_store


def process_document(data: bytes, document: dict):
    text = parse(data)
    chunks_text = chunk_text(text)
    vecs = embed_texts(chunks_text)
    chunks = [
        {
            "text": c, "dense": v['dense'],
            "sparse": v['sparse'], "document_id": document["document_id"],
            "chunk_index": i, "tenant_id": document["tenant_id"],
            "source": document["file_name"]}
        for i, (c, v) in enumerate(zip(chunks_text, vecs))
    ]

    qdrant_store.upsert_chunks(chunks)
    return len(chunks)
