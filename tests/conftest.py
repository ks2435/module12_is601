import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import Base, engine  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def _clean_tables():
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE")
        conn.exec_driver_sql("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def unique_user():
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{suffix}",
        "email": f"user_{suffix}@example.com",
        "password": "s3cret-pass!",
    }


@pytest.fixture
def registered_user(client, unique_user):
    """Register a user and return {id, username, email, password}."""
    r = client.post("/users/register", json=unique_user)
    assert r.status_code == 201, r.text
    body = r.json()
    return {**unique_user, "id": body["id"]}