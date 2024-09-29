import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate
from tests.utils.utils import random_email, random_lower_string


@pytest.mark.usefixtures("db_session")
class TestUsers:
    def test_create_user(self, db_session: Session) -> None:
        email = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=email, password=password)
        user = user_crud.create(db_session, obj_in=user_in)
        assert user.email == email
        assert hasattr(user, "hashed_password")

    def test_get_user(self, db_session: Session) -> None:
        password = random_lower_string()
        username = random_email()
        user_in = UserCreate(email=username, password=password)
        user = user_crud.create(db_session, obj_in=user_in)
        user_2 = user_crud.get(db_session, id=user.id)
        assert user_2
        assert user.email == user_2.email

    def test_create_user_api(self, client: TestClient, db_session: Session) -> None:
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
        self, client: TestClient, db_session: Session
    ) -> None:
        email = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=email, password=password)
        user_crud.create(db_session, obj_in=user_in)
        data = {"email": email, "password": password}
        response = client.post(f"{settings.API_V1_STR}/users/", json=data)
        assert response.status_code == 400, response.text
        assert (
            response.json()["detail"]
            == "The user with this username already exists in the system."
        )
