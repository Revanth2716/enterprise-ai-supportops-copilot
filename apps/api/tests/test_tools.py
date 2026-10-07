import pytest
from app.tools.registry import tool_registry


@pytest.mark.asyncio
async def test_get_customer_tool(db_session):
    res = await tool_registry.execute(
        "get_customer",
        {"customer_identifier": "ACME"},
        session=db_session
    )
    assert res.success is True
    assert res.data["found"] is True
    assert res.data["customer_id"] == "CUST-001"
    assert res.data["tier"] == "Enterprise"


@pytest.mark.asyncio
async def test_get_order_history_detects_duplicates(db_session):
    res = await tool_registry.execute(
        "get_order_history",
        {"customer_id": "CUST-001", "invoice_number": "INV-1042"},
        session=db_session
    )
    assert res.success is True
    assert res.data["found"] is True
    assert res.data["has_duplicate_charges"] is True
    assert len(res.data["duplicate_invoices"]) == 1
    assert res.data["duplicate_invoices"][0]["occurrences"] == 2


@pytest.mark.asyncio
async def test_draft_ticket_tool():
    res = await tool_registry.execute(
        "draft_ticket",
        {
            "customer_id": "CUST-001",
            "title": "Duplicate Charge INV-1042",
            "priority": "P2_HIGH",
            "body": "Reversed $149 duplicate charge",
            "reversal_amount": 149.00,
            "invoice_number": "INV-1042"
        }
    )
    assert res.success is True
    assert res.data["reversal_amount"] == 149.00
    assert "TKT-" in res.data["ticket_id"]
    assert "RESOLUTION DRAFT" in res.data["draft_text"]


@pytest.mark.asyncio
async def test_unauthorized_tool_rejection():
    res = await tool_registry.execute(
        "drop_database_tables",
        {"target": "all"}
    )
    assert res.success is False
    assert "not in authorized tool registry" in res.error
