import pytest


def _payload(user_id, a=10, b=4, op="add"):
    return {"a": a, "b": b, "type": op, "user_id": user_id}


def test_add_calculation(client, registered_user):
    r = client.post("/calculations", json=_payload(registered_user["id"], 10, 4, "add"))
    assert r.status_code == 201
    body = r.json()
    assert body["result"] == 14
    assert body["type"] == "add"
    assert body["user_id"] == registered_user["id"]


@pytest.mark.parametrize(
    "a,b,op,expected",
    [
        (2, 3, "add", 5),
        (10, 4, "subtract", 6),
        (6, 7, "multiply", 42),
        (20, 4, "divide", 5),
    ],
)
def test_all_operations(client, registered_user, a, b, op, expected):
    r = client.post("/calculations", json=_payload(registered_user["id"], a, b, op))
    assert r.status_code == 201
    assert r.json()["result"] == expected


def test_divide_by_zero_rejected(client, registered_user):
    r = client.post(
        "/calculations", json=_payload(registered_user["id"], 5, 0, "divide")
    )
    assert r.status_code == 422


def test_invalid_operation_rejected(client, registered_user):
    r = client.post(
        "/calculations",
        json={"a": 1, "b": 2, "type": "modulo", "user_id": registered_user["id"]},
    )
    assert r.status_code == 422


def test_add_calc_for_missing_user(client):
    r = client.post("/calculations", json=_payload(99999))
    assert r.status_code == 404


def test_browse_calculations(client, registered_user):
    for op in ("add", "subtract", "multiply"):
        client.post("/calculations", json=_payload(registered_user["id"], 2, 3, op))
    r = client.get("/calculations")
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_read_calculation(client, registered_user):
    created = client.post(
        "/calculations", json=_payload(registered_user["id"], 9, 3, "divide")
    ).json()
    r = client.get(f"/calculations/{created['id']}")
    assert r.status_code == 200
    assert r.json()["result"] == 3


def test_read_missing_calculation(client):
    assert client.get("/calculations/99999").status_code == 404


def test_edit_calculation(client, registered_user):
    created = client.post(
        "/calculations", json=_payload(registered_user["id"], 2, 3, "add")
    ).json()
    r = client.put(
        f"/calculations/{created['id']}",
        json={"a": 10, "b": 5, "type": "subtract"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["result"] == 5
    assert body["type"] == "subtract"


def test_edit_partial_keeps_other_fields(client, registered_user):
    created = client.post(
        "/calculations", json=_payload(registered_user["id"], 10, 2, "multiply")
    ).json()
    r = client.put(f"/calculations/{created['id']}", json={"b": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["a"] == 10
    assert body["b"] == 5
    assert body["result"] == 50


def test_edit_divide_by_zero_rejected(client, registered_user):
    created = client.post(
        "/calculations", json=_payload(registered_user["id"], 10, 2, "divide")
    ).json()
    r = client.put(f"/calculations/{created['id']}", json={"b": 0})
    assert r.status_code == 400


def test_delete_calculation(client, registered_user):
    created = client.post(
        "/calculations", json=_payload(registered_user["id"], 1, 1, "add")
    ).json()
    r = client.delete(f"/calculations/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"/calculations/{created['id']}").status_code == 404


def test_delete_missing_calculation(client):
    assert client.delete("/calculations/99999").status_code == 404