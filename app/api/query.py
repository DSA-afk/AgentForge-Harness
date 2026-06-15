from fastapi import APIRouter
from fastapi import Depends
from app.api.document import get_current_claims
from app.config.schema import QueryRequest
from fastapi.concurrency import run_in_threadpool
from app.agent.graph import graph
query_router = APIRouter(prefix="/chat")


@query_router.post("")
async def query(
        request:QueryRequest,
        claims=Depends(get_current_claims),
):
    result = await run_in_threadpool(graph.invoke, {"query": request.query, "tenant_id": claims["tenant_id"]})
    source = [
        d["payload"]["source"]
        for d in result["reranked"]
    ]

    return {"answer": result["answer"],"source": source}