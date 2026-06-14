import uuid
from app.rag.embedding import embed_texts
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, SparseVectorParams,
    Distance, PayloadSchemaType,
    PointStruct, SparseVector,
    Prefetch, FusionQuery,
    Fusion, Filter,
    FieldCondition, MatchValue
)
from qdrant_client.http.exceptions import UnexpectedResponse


class QdrantStore:

    def __init__(self):
        self.collection_name = None
        try:
            self.client = QdrantClient(host="localhost", port=6333)
        except Exception as e:
            raise ConnectionError(f"无法连接到 Qdrant 服务: {e}") from e

    def create_collection(
            self,
            collection_name: str = "documents",
            vector_size: int = 1024,
            recreate_if_exists: bool = False
    ):
        # 检查集合是否存在
        try:
            collection_exists = self.client.collection_exists(collection_name)

            if collection_exists:
                if recreate_if_exists:
                    print(f"集合 {collection_name} 已存在，正在删除...")
                    try:
                        self.client.delete_collection(collection_name)
                    except Exception as e:
                        raise ConnectionError(f"无法删除集合 {collection_name}: {e}") from e
                else:
                    print(f"集合 {collection_name} 已存在，直接返回客户端")
                    self.collection_name = collection_name
                    return self.client
        except UnexpectedResponse as e:
            print(f"检查集合状态时出错（Qdrant 服务可能未正常响应）: {e}")
            raise
        except Exception as e:
            print(f"检查集合时发生未知错误: {e}")
            raise

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": VectorParams(size=vector_size, distance=Distance.COSINE)},
                sparse_vectors_config={
                    "sparse": SparseVectorParams(),
                }
            )
            # 对 tenant_id 建 payload 索引：多租户过滤才高效（否则每次全扫）
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="tenant_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            print(f"集合{collection_name}创建成功")
            self.collection_name = collection_name
            return self.client
        except ValueError as e:
            # 参数错误（如 size 不是整数）
            print(f"参数配置错误: {e}")
            raise
        except Exception as e:
            print(f"创建集合时发生未知错误: {e}")
            raise

    def upsert_chunks(self, chunks: list[dict]):
        points = [PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "dense": chunk['dense'],
                "sparse": SparseVector(indices=chunk['sparse']['indices'], values=chunk['sparse']['values'])
            },
            payload={
                "text": chunk["text"],
                "document_id": chunk['document_id'],
                "chunk_index": chunk['chunk_index'],
                "tenant_id": chunk['tenant_id'],
                "source": chunk['source'],
            }
        ) for chunk in chunks]

        self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points,
        )

    def hybrid_search(self, query_text: str, tenant_id: str, limit: int = 50):
        q_vector = embed_texts([query_text])[0]
        prefetch = [
                Prefetch(query=q_vector['dense'], using='dense', limit=limit),
                Prefetch(
                    query=SparseVector(
                        indices=q_vector['sparse']['indices'],
                        values=q_vector['sparse']['values']),
                    using='sparse',
                    limit=limit
                )
            ]
        q_fusion = FusionQuery(fusion=Fusion.RRF)
        q_filter = Filter(
            must=[FieldCondition(key="tenant_id",match=MatchValue(value=tenant_id))]
        )

        resp = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=prefetch,
            query=q_fusion,
            query_filter=q_filter,
            limit=limit,
            with_payload=True,
        )

        return resp.points

    def get_collection(self, collection_name: str):
        collection_info = self.client.get_collection(collection_name)
        print(f"状态: {collection_info.status}")
        print(f"点数量: {collection_info.points_count}")
        print(f"已索引向量数: {collection_info.indexed_vectors_count}")
        print(f"分段数: {collection_info.segments_count}")
        print(f"dense 向量配置: {collection_info.config.params.vectors}")
        print(f"sparse 向量配置: {collection_info.config.params.sparse_vectors}")
        print(f"payload 索引: {collection_info.payload_schema}")
        return collection_info


if __name__ == '__main__':
    qdrant_client = QdrantStore()
    qdrant_client.create_collection("documents", recreate_if_exists=True)
    qdrant_client.get_collection("documents")
