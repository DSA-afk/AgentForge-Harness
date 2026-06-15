from fastapi import FastAPI
from app.api.health import health_router
from app.api.auth import auth_router
from app.api.document import d_router
from app.api.query import query_router
app = FastAPI()


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(d_router)
app.include_router(query_router)