from typing import Generator, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.crud.user import user as user_crud
from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.token import TokenPayload
from app.core import security
from app.core.config import settings
from app.db.db_utils import DatabaseConnectionPool

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    db_pool = DatabaseConnectionPool()
    db = db_pool.get_session()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = cast(CRUDUser, user_crud).get(db, id=token_data.sub)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return cast(User, user)


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not cast(CRUDUser, user_crud).is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not cast(CRUDUser, user_crud).is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
