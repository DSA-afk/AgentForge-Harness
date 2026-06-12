from fastapi import APIRouter, Depends
from app.api.auth import get_tenant_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


health_router = APIRouter(prefix="/health")


@health_router.get("")
async def health_check():
    return {"status": "ok"}


@health_router.get("/document")
async def db_document(session: AsyncSession = Depends(get_tenant_db)):

    result = (await session.execute(text("SELECT * from document"))).mappings().all()
    return {"result": [dict(r) for r in result]}
