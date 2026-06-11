from fastapi import APIRouter, Depends
from ..database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter(prefix="/health")


@router.get("/")
async def health_check():
    return {"status": "ok"}


@router.get("/document")
async def db_document(session: AsyncSession = Depends(get_db)):
    result = (await session.execute(text("SELECT * from document"))).mappings().all()

    return {"result": [dict(r) for r in result]}
