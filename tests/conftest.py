import pytest
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from fastapi.testclient import TestClient
from typing import Generator, Dict, Any, cast

from app.db.base import Base
from app.core.config import settings
from main import app
from app.api import deps
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, None, None]:
    engine = create_engine(str(settings.TEST_SQLALCHEMY_DATABASE_URI))
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, db_session: Session) -> Dict[str, str]:
    email = settings.FIRST_SUPERUSER
    password = settings.FIRST_SUPERUSER_PASSWORD

    if email is None or password is None:
        raise ValueError("FIRST_SUPERUSER or FIRST_SUPERUSER_PASSWORD is not set")

    logger.debug(f"Creating superuser with email: {email}")
    superuser = UserCreate(
        email=email,
        password=password,
        is_superuser=True,
    )
    try:
        user = user_crud.create(db=db_session, obj_in=superuser)
        logger.debug(f"Superuser created with id: {user.id}")
    except Exception as e:
        logger.error(f"Error creating superuser: {str(e)}")
        raise

    login_data = {
        "username": email,
        "password": password,
    }
    logger.debug("Attempting to log in superuser")
    try:
        r = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data=cast(Dict[str, Any], login_data),
        )
        logger.debug(f"Login response status code: {r.status_code}")
        logger.debug(
            "Login response content: %s",
            r.content.decode("utf-8") if isinstance(r.content, bytes) else r.content,
        )
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise

    tokens = r.json()
    if "access_token" not in tokens:
        logger.error(f"Access token not found in response. Response: {tokens}")
        raise ValueError("Access token not found in login response")

    a_token = tokens["access_token"]
    logger.debug(
        "Successfully obtained access token: %s...",
        a_token[:10] if isinstance(a_token, str) else str(a_token[:10]),
    )

    # Handle potential bytes object
    token_str = a_token.decode("utf-8") if isinstance(a_token, bytes) else a_token
    return {"Authorization": f"Bearer {token_str}"}
