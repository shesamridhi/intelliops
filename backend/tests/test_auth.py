def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={
        "email": "admin@intelliops.com",
        "password": "supersecret123",
        "full_name": "Admin User",
        "role": "admin",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "admin@intelliops.com"

    resp = client.post("/api/auth/login", json={
        "email": "admin@intelliops.com",
        "password": "supersecret123",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={
        "email": "user@intelliops.com",
        "password": "correctpassword",
        "full_name": "User",
        "role": "staff",
    })
    resp = client.post("/api/auth/login", json={
        "email": "user@intelliops.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_duplicate_registration_rejected(client):
    payload = {
        "email": "dup@intelliops.com",
        "password": "supersecret123",
        "full_name": "Dup User",
        "role": "staff",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 400
