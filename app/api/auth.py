from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import uuid
from app.config.schema import RegisterRequest, LoginRequest
from app.database.session import AsyncSessionLocal
from sqlalchemy import text
from app.auth.security import hash_password
from fastapi import HTTPException
from app.auth.security import verify_password
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.jwt import decode_token

auth_router = APIRouter(prefix="/auth")
security = HTTPBearer()


async def get_current_claims(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(401, "无效或已过期的 token", headers={"WWW-Authenticate": "Bearer"})

    if payload.get("type") != "access":
        raise HTTPException(401, "需要 access token", headers={"WWW-Authenticate": "Bearer"})

    sub = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if not sub or not tenant_id:
        raise HTTPException(401, "token 缺少必要信息", headers={"WWW-Authenticate": "Bearer"})

    return {"sub": sub, "tenant_id": tenant_id}


async def get_tenant_db(claims=Depends(get_current_claims)):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_config('app.current_tenant',:tid,true)"),
                {"tid": claims["tenant_id"]}
            )
            yield session


@auth_router.post("/register")
async def register(request: RegisterRequest):
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    hash_pswd = hash_password(request.password)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tid , true)"),
                {"tid": tenant_id}
            )

            await session.execute(
                text("INSERT INTO tenant (id, name) VALUES (:id, :name)"),
                {"id": tenant_id, "name": request.company_name}
            )
            try:
                await session.execute(
                    text("INSERT INTO users (id,tenant_id,name,email,hash_pswd) "
                         "VALUES (:id, :tenant_id, :name, :email, :hash_pswd)"),
                    {"id": user_id, "tenant_id": tenant_id, "name": request.user_name,
                     "email": request.email, "hash_pswd": hash_pswd}
                )
            except IntegrityError as e:
                raise HTTPException(409, "邮箱已存在")

    return {"tenant_id": tenant_id, "user_id": user_id, "email": request.email}


@auth_router.post("/login")
async def login(request: LoginRequest):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_config('app.current_tenant',:tid,true)"),
                {"tid": request.tenant_id}
            )

            result = await session.execute(
                text("SELECT id,hash_pswd FROM users WHERE email = :email"),
                {"email": request.email}
            )

            data = result.first()

            if data is None:
                raise HTTPException(401, "邮箱或密码错误")
            if not verify_password(request.password, data.hash_pswd):
                raise HTTPException(401, "邮箱或密码错误")

            access_token = create_access_token({"sub": data.id, "tenant_id": request.tenant_id})
            refresh_token = create_refresh_token({"sub": data.id, "tenant_id": request.tenant_id})

            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post("/refresh")
async def refresh(credentials: HTTPAuthorizationCredentials = Depends(security)):
    refresh_token = credentials.credentials

    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(401, "无效或已过期的 token", headers={"WWW-Authenticate": "Bearer"})

    if payload.get("type") != "refresh":
        raise HTTPException(401, "需要 refresh token", headers={"WWW-Authenticate": "Bearer"})

    sub = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if not sub or not tenant_id:
        raise HTTPException(401, "token 缺少必要信息", headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token({"sub": sub, "tenant_id": tenant_id})

    return {"access_token": access_token, "token_type": "bearer"}
