from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from typing import Any, Annotated, cast, Sequence, Optional

from app.crud.user import user as user_crud
from app.core.security import verify_password
from app.schemas.user import UserCreate, UserUpdate, UserFilterParams, UserVerify
from app.schemas.user import User as user_schema
from app.models.user import User as user_model
from app.api import deps

router = APIRouter()


@router.post("/", response_model=user_schema, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = user_crud.get_by_filter(db, filter_params={"email": user_in.email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists in the system.",
        )
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.get("/", response_model=Sequence[user_schema], status_code=status.HTTP_200_OK)
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_superuser: Optional[bool] = Query(
        None, description="Filter by superuser status"
    ),
    email: Optional[str] = Query(None, description="Filter by email"),
) -> Sequence[user_model]:
    """
    Retrieve users with optional filtering.
    """
    filter_params = UserFilterParams(
        is_active=is_active, is_superuser=is_superuser, email=email
    ).model_dump(exclude_none=True)

    users = user_crud.get_multi(db, skip=skip, limit=limit, filter_params=filter_params)
    return users


@router.get("/{user_id}", response_model=user_schema, status_code=status.HTTP_200_OK)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get(
    "/by-email/{email}", response_model=user_schema, status_code=status.HTTP_200_OK
)
def read_user_by_email(
    email: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by email.
    """
    user = user_crud.get_by_filter(db, filter_params={"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=user_schema, status_code=status.HTTP_200_OK)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    try:
        user = user_crud.update(db, db_obj=user, obj_in=user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete a user.
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user_crud.remove(db, id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/verify", response_model=user_schema)
def verify_user_credentials(
    user_in: UserVerify, db: Annotated[Session, Depends(deps.get_db)]
) -> user_model:
    """
    Verify user credentials and return user information if valid.
    """
    user = user_crud.get_by_filter(db, filter_params={"email": user_in.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Cast to proper type to help mypy understand the model type
    user = cast(user_model, user)

    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user
