from app.config.schema import AgentState
from langgraph.graph import StateGraph, START, END
from app.agent.llm import chat
from app.rag.qdrant_store import qdrant_store
from app.rag.reranker import rerank


# 生成
def generate(state: AgentState):
    context = "\n\n".join(
        f"【资料{i+1}｜来源：{r['payload']['source']}】\n{r['text']}"
        for i, r in enumerate(state["reranked"])
    )
    messages = [
        {"role": "system", "content": "你是知识库问答助手，只能依据下面【参考资料】回答；若资料中没有答案，明确说'根据现有资料无法回答'，不要编造；回答末尾标注引用的资料编号。"},
        {"role": "user", "content": f"【参考资料】\n{context}\n\n【问题】\n{state['query']}"},
    ]
    answer = chat(messages)
    return {"answer": answer}


# 检索
def retrieve(state: AgentState):
    retrieved = qdrant_store.hybrid_search(state["query"], state["tenant_id"], limit=50)
    return {"retrieved": retrieved}


# 精排
def rerank_node(state: AgentState):
    reranked = rerank(state["query"], state["retrieved"])
    return {"reranked": reranked}


builder = StateGraph(AgentState)
builder.add_node("generate", generate)
builder.add_node("retrieve", retrieve)
builder.add_node("rerank_node", rerank_node)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "rerank_node")
builder.add_edge("rerank_node", "generate")
builder.add_edge("generate", END)

graph = builder.compile()
