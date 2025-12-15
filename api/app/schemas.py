from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from .models import UserRole, UserStatus

# --- Schemas de Token (Login) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Schemas de Usuario ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

# Esto es lo que devolverá la API al consultar un usuario (sin password)
class UserResponse(UserBase):
    id: UUID
    role: UserRole
    status: UserStatus

    class Config:
        from_attributes = True # Antes orm_mode = True


class UserInvite(BaseModel):
    email: EmailStr

class InviteResponse(BaseModel):
    email: str
    temp_password: str # Devolvemos esto solo por ahora para testear sin enviar email real
    message: str


class ProfileCreate(BaseModel):
    company_name: str
    legal_id: str
    address: dict  # JSON con la dirección
    contact_person: str
    sector: str

class ProfileResponse(ProfileCreate):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True


class DeploymentResponse(BaseModel):
    did: str
    connector_url: str
    identity_hub_url: str
    has_api_key: bool = True
    class Config:
        from_attributes = True

class DeploymentSecretResponse(DeploymentResponse):
    api_key: str