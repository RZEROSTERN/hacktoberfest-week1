from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item_with_query():
    response = client.get("/items/42", params={"q": "search"})
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "search"}


def test_read_item_without_query():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": None}


def test_read_item_rejects_non_integer_id():
    response = client.get("/items/abc")
    assert response.status_code == 422
