import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    assert settings.FIRST_SUPERUSER, "FIRST_SUPERUSER is not set in the settings"
    assert (
        settings.FIRST_SUPERUSER_PASSWORD
    ), "FIRST_SUPERUSER_PASSWORD is not set in the settings"

    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    # Remove None values and ensure all values are strings
    login_data = {k: str(v) for k, v in login_data.items() if v is not None}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
