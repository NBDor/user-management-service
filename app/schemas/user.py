from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.security import get_password_hash
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_active: bool = True
    is_superuser: bool = False

    @field_validator("password")
    def hash_password(cls, v: str) -> str:
        return get_password_hash(v)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("password")
    def hash_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return get_password_hash(v)
        return v


class UserInDBBase(UserBase):
    id: int

    model_config = {"from_attributes": True}


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password: str
