from fastapi import FastAPI
from app.api.health import health_router
from app.api.auth import auth_router
app = FastAPI()


app.include_router(health_router)
app.include_router(auth_router)