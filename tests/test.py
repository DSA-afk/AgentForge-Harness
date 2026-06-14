from app.rag.qdrant_store import QdrantStore
from app.rag.embedding import embed_texts

client = QdrantStore()

client.create_collection("documents")
raw = [
    # ---- 租户 A（某 SaaS 公司知识库）----
    {"text": "本公司支持7天无理由退款，款项将在3个工作日内原路退回到您的支付账户",
     "tenant_id": "tenant-a", "document_id": "doc-refund", "chunk_index": 0, "source": "退款政策 v2"},
    {"text": "线上服务通过 Kubernetes（K8s）的 Deployment 部署，支持滚动更新与自动扩缩容",
     "tenant_id": "tenant-a", "document_id": "doc-ops", "chunk_index": 0, "source": "运维手册"},
    {"text": "如需开具增值税专用发票，请在订单完成后30天内提交申请，发票以电子形式发送",
     "tenant_id": "tenant-a", "document_id": "doc-invoice", "chunk_index": 0, "source": "财务FAQ"},

    # ---- 租户 B（另一家公司，内容完全不同）----
    {"text": "员工申请年假需提前3个工作日在OA系统提交，由直属上级审批后生效",
     "tenant_id": "tenant-b", "document_id": "doc-leave", "chunk_index": 0, "source": "考勤制度"},
    {"text": "差旅费报销须附发票原件与审批单，财务部每周三统一处理报销申请",
     "tenant_id": "tenant-b", "document_id": "doc-expense", "chunk_index": 0, "source": "报销指南"},
]

q_vector = embed_texts([q['text'] for q in raw])

for i, vector in enumerate(q_vector):
    raw[i]["dense"] = vector["dense"]
    raw[i]["sparse"] = vector["sparse"]


client.upsert_chunks(raw)

resp = client.hybrid_search("怎么把钱要回来","tenant-a")
print(resp)

resp = client.hybrid_search("K8s 部署","tenant-a")
print(resp)

resp = client.hybrid_search("怎么把钱要回来","tenant-b")
print(resp)
