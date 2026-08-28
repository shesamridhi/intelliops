from app.ai_agent import _pick_tool_rule_based


def test_rule_based_routes_low_stock_query():
    assert _pick_tool_rule_based("which items are low on stock?") == "low_stock_items"


def test_rule_based_routes_pending_orders_query():
    assert _pick_tool_rule_based("how many pending orders do we have") == "pending_orders_count"


def test_rule_based_routes_inventory_value_query():
    assert _pick_tool_rule_based("what is our inventory worth") == "inventory_value"


def test_rule_based_returns_none_for_unrelated_query():
    assert _pick_tool_rule_based("what's the weather today") is None


def test_agent_end_to_end_via_api(client):
    resp = client.post("/api/auth/register", json={
        "email": "agent@intelliops.com", "password": "supersecret123",
        "full_name": "Agent Tester", "role": "admin",
    })
    token = client.post("/api/auth/login", json={
        "email": "agent@intelliops.com", "password": "supersecret123",
    }).json()["access_token"]

    resp = client.post(
        "/api/agent/query",
        json={"prompt": "show me low stock items"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider_used"] == "fallback-rule-based"
    assert "actions_taken" in body
