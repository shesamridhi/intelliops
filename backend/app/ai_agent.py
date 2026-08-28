"""
Agentic AI module.

Design goals (talk about these in the interview):
1. Provider-agnostic: swap OpenAI / Anthropic / a local fallback via one
   config flag (LLM_PROVIDER) — no other code changes needed. This mirrors
   how you'd wire in a framework like Google Antigravity in production:
   the agent orchestration layer shouldn't care which model executes it.
2. Tool-calling / function-calling pattern: the agent doesn't hallucinate
   business data — it decides which internal "tool" (DB query function) to
   call, executes it against Postgres, then grounds its answer in the
   real result. This is the core idea behind agentic (vs. plain chat) AI.
3. Graceful degradation: if no API key is configured, a deterministic
   rule-based agent still answers common ops questions using the same
   tools, so the demo/interview never breaks on a missing key.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import get_settings
from app.models import InventoryItem, Order, OrderStatus

settings = get_settings()


# ---------------- Tools the agent can call ----------------

def tool_low_stock_items(db: Session) -> list[dict]:
    items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.reorder_threshold
    ).all()
    return [{"sku": i.sku, "name": i.name, "quantity": i.quantity} for i in items]


def tool_pending_orders_count(db: Session) -> int:
    return db.query(Order).filter(Order.status == OrderStatus.PENDING).count()


def tool_inventory_value(db: Session) -> float:
    total = db.query(func.sum(InventoryItem.quantity * InventoryItem.unit_price)).scalar()
    return float(total or 0)


TOOLS = {
    "low_stock_items": tool_low_stock_items,
    "pending_orders_count": tool_pending_orders_count,
    "inventory_value": tool_inventory_value,
}

TOOL_DESCRIPTIONS = """
Available tools:
- low_stock_items(): returns inventory items at/below reorder threshold
- pending_orders_count(): returns count of orders awaiting processing
- inventory_value(): returns total value of current inventory
"""


def _pick_tool_rule_based(prompt: str) -> str | None:
    p = prompt.lower()
    if "reorder" in p or "restock" in p or ("low" in p and "stock" in p):
        return "low_stock_items"
    if "pending" in p and "order" in p:
        return "pending_orders_count"
    if "value" in p or "worth" in p:
        return "inventory_value"
    return None


def run_agent(prompt: str, db: Session) -> dict:
    """
    Returns {answer, provider_used, actions_taken}.
    Falls back safely if no LLM API key is present.
    """
    provider = settings.LLM_PROVIDER
    actions_taken: list[str] = []

    # Step 1: decide which tool to call (LLM-driven if key present, else rule-based)
    tool_name = None
    if provider == "openai" and settings.OPENAI_API_KEY:
        tool_name = _select_tool_via_openai(prompt)
        provider_used = "openai"
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        tool_name = _select_tool_via_anthropic(prompt)
        provider_used = "anthropic"
    else:
        tool_name = _pick_tool_rule_based(prompt)
        provider_used = "fallback-rule-based"

    # Step 2: execute the chosen tool against the real database
    tool_result = None
    if tool_name and tool_name in TOOLS:
        tool_result = TOOLS[tool_name](db)
        actions_taken.append(f"called tool: {tool_name}")

    # Step 3: compose a grounded natural-language answer
    answer = _compose_answer(prompt, tool_name, tool_result)
    return {"answer": answer, "provider_used": provider_used, "actions_taken": actions_taken}


def _compose_answer(prompt: str, tool_name: str | None, tool_result) -> str:
    if tool_name == "low_stock_items":
        if not tool_result:
            return "All inventory items are currently above their reorder threshold. No restocking needed."
        items = ", ".join(f"{i['name']} ({i['quantity']} left)" for i in tool_result)
        return f"{len(tool_result)} item(s) need restocking: {items}."
    if tool_name == "pending_orders_count":
        return f"There are currently {tool_result} pending order(s) awaiting processing."
    if tool_name == "inventory_value":
        return f"Total current inventory value is ${tool_result:,.2f}."
    return (
        "I can help with inventory and order questions — try asking about "
        "'low stock items', 'pending orders', or 'inventory value'."
    )


def _select_tool_via_openai(prompt: str) -> str | None:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You route user prompts to internal tools.\n{TOOL_DESCRIPTIONS}\nReply with ONLY the tool name, or 'none'."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    name = resp.choices[0].message.content.strip()
    return name if name in TOOLS else None


def _select_tool_via_anthropic(prompt: str) -> str | None:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        system=f"You route user prompts to internal tools.\n{TOOL_DESCRIPTIONS}\nReply with ONLY the tool name, or 'none'.",
        messages=[{"role": "user", "content": prompt}],
    )
    name = resp.content[0].text.strip()
    return name if name in TOOLS else None
