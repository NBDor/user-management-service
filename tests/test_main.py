from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item() -> None:
    response = client.get("/items/42", params={"q": "test"})
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}
