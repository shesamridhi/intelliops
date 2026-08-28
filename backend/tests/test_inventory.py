def _register_and_login(client, role="staff", email="x@intelliops.com"):
    client.post("/api/auth/register", json={
        "email": email, "password": "supersecret123", "full_name": "X", "role": role,
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def test_staff_cannot_create_inventory_item(client):
    token = _register_and_login(client, role="staff", email="staff@intelliops.com")
    resp = client.post(
        "/api/inventory",
        json={"sku": "SKU-1", "name": "Widget", "quantity": 100},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403  # RBAC enforced


def test_admin_can_create_inventory_item(client):
    token = _register_and_login(client, role="admin", email="admin2@intelliops.com")
    resp = client.post(
        "/api/inventory",
        json={"sku": "SKU-2", "name": "Gadget", "quantity": 50, "unit_price": 9.99},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["sku"] == "SKU-2"


def test_duplicate_sku_rejected(client):
    token = _register_and_login(client, role="admin", email="admin3@intelliops.com")
    payload = {"sku": "SKU-3", "name": "Item", "quantity": 10}
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/api/inventory", json=payload, headers=headers).status_code == 201
    assert client.post("/api/inventory", json=payload, headers=headers).status_code == 400


def test_list_requires_authentication(client):
    resp = client.get("/api/inventory")
    assert resp.status_code == 401
