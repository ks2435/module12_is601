from sqlalchemy import text

from database import engine


def test_register_user_success(client, unique_user):
    r = client.post("/users/register", json=unique_user)
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == unique_user["username"]
    assert body["email"] == unique_user["email"]
    assert "password" not in body
    assert "password_hash" not in body


def test_register_persists_hashed_password(client, unique_user):
    client.post("/users/register", json=unique_user)
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT password_hash FROM users WHERE username = :u"),
            {"u": unique_user["username"]},
        ).fetchone()
    assert row is not None
    assert row.password_hash != unique_user["password"]
    assert row.password_hash.startswith("$2")


def test_register_duplicate_username_rejected(client, unique_user):
    assert client.post("/users/register", json=unique_user).status_code == 201
    dup = {**unique_user, "email": "different@example.com"}
    assert client.post("/users/register", json=dup).status_code == 400


def test_register_invalid_email_rejected(client):
    r = client.post(
        "/users/register",
        json={"username": "x", "email": "not-an-email", "password": "pw"},
    )
    assert r.status_code == 422


def test_login_success(client, unique_user):
    client.post("/users/register", json=unique_user)
    r = client.post(
        "/users/login",
        json={"username": unique_user["username"], "password": unique_user["password"]},
    )
    assert r.status_code == 200
    assert r.json()["username"] == unique_user["username"]


def test_login_wrong_password(client, unique_user):
    client.post("/users/register", json=unique_user)
    r = client.post(
        "/users/login",
        json={"username": unique_user["username"], "password": "WRONG"},
    )
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post(
        "/users/login", json={"username": "nobody", "password": "whatever"}
    )
    assert r.status_code == 401