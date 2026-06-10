from fastapi import APIRouter,Depends
from ..database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter(prefix="/health")


@router.get("/")
async def health_check():
    return {"status": "ok"}


@router.get("/db")
async def db_check(session:AsyncSession = Depends(get_db)):
    result = await session.execute(text("SELECT * from document"))

    return {"result":result.scalar()}
