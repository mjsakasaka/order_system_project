import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def login_and_get_token(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token(client):
    return login_and_get_token(client, "admin", "admin123")


@pytest.fixture(scope="session")
def cs_token(client):
    return login_and_get_token(client, "cs", "cs123")


@pytest.fixture(scope="session")
def wh_token(client):
    return login_and_get_token(client, "wh", "wh123")


@pytest.fixture()
def make_order(client, admin_token):
    """
    每个测试需要订单时调用：order_id = make_order()
    """
    def _make():
        resp = client.post(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200, resp.text
        return resp.json()["id"]
    return _make


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
