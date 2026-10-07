from typing import Optional, Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Customer


async def get_customer(identifier: str, session: AsyncSession) -> Dict[str, Any]:
    """
    Looks up a customer profile by Name or Account Number.
    """
    identifier_clean = identifier.strip()
    stmt = select(Customer).where(
        or_(
            Customer.account_number.ilike(f"%{identifier_clean}%"),
            Customer.name.ilike(f"%{identifier_clean}%")
        )
    )
    res = await session.execute(stmt)
    cust = res.scalars().first()

    if not cust:
        return {
            "found": False,
            "message": f"Customer '{identifier}' was not found in enterprise CRM."
        }

    return {
        "found": True,
        "customer_id": cust.id,
        "name": cust.name,
        "account_number": cust.account_number,
        "tier": cust.tier,
        "status": cust.status,
        "support_pin": cust.support_pin,
        "primary_contact": cust.primary_contact
    }
