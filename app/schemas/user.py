from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.core.security import get_password_hash


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    def create_update_dict(self) -> Dict[str, Any]:
        """Convert to dict and transform password to hashed_password."""
        data = self.model_dump()
        if "password" in data:
            password = data.pop("password")
            data["hashed_password"] = get_password_hash(password)
        return data


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None

    def create_update_dict(self) -> Dict[str, Any]:
        """Convert to dict and handle password if present."""
        data = self.model_dump(exclude_none=True)
        if "password" in data and data["password"] is not None:
            password = data.pop("password")
            data["hashed_password"] = get_password_hash(password)
        return data


class UserInDBBase(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class UserFilterParams(BaseModel):
    """Schema for user filtering parameters"""

    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)


class UserVerify(BaseModel):
    """Schema for user credential verification"""

    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")
