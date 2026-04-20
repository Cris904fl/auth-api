from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr


class AuthProvider(str, Enum):
    local = "local"
    google = "google"


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: UserRole
    provider: AuthProvider
    created_at: str


class User(BaseModel):
    user_id: str = ""
    email: str
    full_name: str
    hashed_password: Optional[str] = None
    role: UserRole = UserRole.user
    provider: AuthProvider = AuthProvider.local
    created_at: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        if not self.user_id:
            self.user_id = str(uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dynamo(self) -> dict:
        return self.model_dump()

    def to_out(self) -> UserOut:
        return UserOut(
            user_id=self.user_id,
            email=self.email,
            full_name=self.full_name,
            role=self.role,
            provider=self.provider,
            created_at=self.created_at,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
