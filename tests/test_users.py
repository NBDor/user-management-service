import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Tuple

from app.core.config import settings
from app.crud.user import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


@pytest.fixture
def test_user(db_session: Session) -> Tuple[User, str]:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_crud.create(db_session, obj_in=user_in)
    return user, password


def test_create_user(db_session: Session) -> None:
    """Test user creation via CRUD operation."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_crud.create(db_session, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "password")
    assert user.password != password  # Check that password is hashed


def test_get_user(db_session: Session, test_user: Tuple[User, str]) -> None:
    """Test retrieving a user by ID."""
    user, _ = test_user
    user_2 = user_crud.get(db_session, id=user.id)
    assert user_2
    assert user.email == user_2.email


def test_get_user_by_email(db_session: Session, test_user: Tuple[User, str]) -> None:
    """Test retrieving a user by email."""
    user, _ = test_user
    user_2 = user_crud.get_by_email(db_session, email=user.email)
    assert user_2
    assert user.id == user_2.id


def test_update_user(db_session: Session, test_user: Tuple[User, str]) -> None:
    """Test updating a user."""
    user, _ = test_user
    new_email = random_email()
    user_update = UserUpdate(email=new_email)
    updated_user = user_crud.update(db_session, db_obj=user, obj_in=user_update)
    assert updated_user.email == new_email


def test_delete_user(db_session: Session) -> None:
    """Test deleting a user."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_crud.create(db_session, obj_in=user_in)
    user_2 = user_crud.remove(db_session, id=user.id)
    user_3 = user_crud.get(db_session, id=user.id)
    assert user_2 is not None
    assert user_3 is None


def test_create_user_api(client: TestClient, db_session: Session) -> None:
    """Test user creation via API."""
    email = random_email()
    password = random_lower_string()
    data = {"email": email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert response.status_code == 201, response.text
    created_user = response.json()
    user = user_crud.get_by_email(db_session, email=email)
    assert user
    assert user.email == created_user["email"]


def test_create_user_existing_email(
    client: TestClient, db_session: Session, test_user: Tuple[User, str]
) -> None:
    """Test creating a user with an existing email."""
    user, password = test_user
    data = {"email": user.email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert response.status_code == 409, response.text
    assert (
        response.json()["detail"]
        == "The user with this email already exists in the system."
    )


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("notanemail", "password123", 422),
        ("valid@email.com", "short", 422),
        ("", "password123", 422),
        ("valid@email.com", "", 422),
    ],
)
def test_create_user_invalid_input(
    client: TestClient, email: str, password: str, status_code: int
) -> None:
    """Test creating a user with invalid input."""
    data = {"email": email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert response.status_code == status_code


def test_get_users(client: TestClient, test_user: Tuple[User, str]) -> None:
    """Test retrieving all users."""
    response = client.get(f"{settings.API_V1_STR}/users/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_user_by_id_api(client: TestClient, test_user: Tuple[User, str]) -> None:
    """Test retrieving a user by ID via API."""
    user, _ = test_user
    response = client.get(f"{settings.API_V1_STR}/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_update_user_api(client: TestClient, test_user: Tuple[User, str]) -> None:
    """Test updating a user via API."""
    user, _ = test_user
    new_email = random_email()
    data = {"email": new_email}
    response = client.put(f"{settings.API_V1_STR}/users/{user.id}", json=data)
    assert response.status_code == 200
    assert response.json()["email"] == new_email


def test_delete_user_api(client: TestClient, db_session: Session) -> None:
    """Test deleting a user via API."""
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_crud.create(db_session, obj_in=user_in)
    response = client.delete(f"{settings.API_V1_STR}/users/{user.id}")
    assert response.status_code == 204
    user_2 = user_crud.get(db_session, id=user.id)
    assert user_2 is None
