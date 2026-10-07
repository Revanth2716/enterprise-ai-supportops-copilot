from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Order


async def get_order_history(
    customer_id: str,
    invoice_number: Optional[str],
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Retrieves orders/invoices for a customer and detects billing anomalies
    such as duplicate payment charges.
    """
    stmt = select(Order).where(Order.customer_id == customer_id)
    if invoice_number:
        stmt = stmt.where(Order.invoice_number.ilike(f"%{invoice_number.strip()}%"))

    stmt = stmt.order_by(Order.billing_date.desc())
    res = await session.execute(stmt)
    orders = res.scalars().all()

    if not orders:
        return {
            "found": False,
            "total_orders": 0,
            "orders": [],
            "message": f"No order records found for customer '{customer_id}'."
        }

    # Group by invoice number to detect duplicate charges
    invoice_counts: Dict[str, List[Order]] = {}
    for o in orders:
        invoice_counts.setdefault(o.invoice_number, []).append(o)

    duplicate_invoices = []
    for inv, ord_list in invoice_counts.items():
        if len(ord_list) > 1:
            duplicate_invoices.append({
                "invoice_number": inv,
                "occurrences": len(ord_list),
                "total_charged": sum(float(x.amount) for x in ord_list),
                "transactions": [
                    {
                        "order_id": x.id,
                        "amount": float(x.amount),
                        "reference": x.transaction_reference,
                        "date": x.billing_date.isoformat(),
                        "notes": x.notes
                    }
                    for x in ord_list
                ]
            })

    order_records = [
        {
            "order_id": o.id,
            "invoice_number": o.invoice_number,
            "amount": float(o.amount),
            "currency": o.currency,
            "status": o.status,
            "transaction_reference": o.transaction_reference,
            "billing_date": o.billing_date.isoformat(),
            "notes": o.notes
        }
        for o in orders
    ]

    return {
        "found": True,
        "total_orders": len(orders),
        "has_duplicate_charges": len(duplicate_invoices) > 0,
        "duplicate_invoices": duplicate_invoices,
        "orders": order_records
    }
