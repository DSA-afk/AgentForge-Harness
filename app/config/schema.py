from pydantic import BaseModel


class RegisterRequest(BaseModel):
    company_name: str

    user_name:str
    email: str
    password: str


class LoginRequest(BaseModel):
    tenant_id: str

    email: str
    password: str