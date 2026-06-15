from pydantic import BaseModel
from typing import TypedDict


class RegisterRequest(BaseModel):
    company_name: str

    user_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    tenant_id: str

    email: str
    password: str


class AgentState(TypedDict):
    messages: list
    query: str
    answer: str
    tenant_id: str  # 检索要按租户过滤
    retrieved: list  # 召回的候选
    reranked: list # 精排后的 top-k


class QueryRequest(BaseModel):
    query: str
