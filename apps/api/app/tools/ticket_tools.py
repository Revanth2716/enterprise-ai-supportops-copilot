import uuid
from typing import Dict, Any


def draft_ticket(
    customer_id: str,
    title: str,
    priority: str,
    body: str,
    reversal_amount: float = 0.0,
    invoice_number: str = ""
) -> Dict[str, Any]:
    """
    Prepares a structured support resolution draft ticket for operator review.
    Does not commit write directly to external CRM, strictly staging the draft.
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"

    formatted_draft = (
        f"--- RESOLUTION DRAFT ({ticket_id}) ---\n"
        f"Customer ID: {customer_id}\n"
        f"Subject: {title}\n"
        f"Priority: {priority.upper()}\n"
        f"Invoice: {invoice_number or 'N/A'}\n"
        f"Adjustment Amount: ${reversal_amount:.2f}\n\n"
        f"Customer Response Draft:\n{body}\n"
        f"----------------------------------------"
    )

    return {
        "success": True,
        "ticket_id": ticket_id,
        "title": title,
        "priority": priority,
        "reversal_amount": reversal_amount,
        "invoice_number": invoice_number,
        "status": "drafted",
        "draft_text": formatted_draft
    }
