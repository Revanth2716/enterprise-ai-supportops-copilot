import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.models import User, Customer, Order, KnowledgeDocument, DocumentChunk
from datetime import datetime, timezone

# Use fast in-memory sqlite database for unit tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        # Seed test customers
        cust1 = Customer(
            id="CUST-001",
            account_number="ACC-ACME-901",
            name="ACME Corporation",
            tier="Enterprise",
            status="active"
        )
        cust2 = Customer(
            id="CUST-002",
            account_number="ACC-GLOB-412",
            name="Globex International",
            tier="Enterprise",
            status="active"
        )
        cust3 = Customer(
            id="CUST-003",
            account_number="ACC-INIT-773",
            name="Initech Systems",
            tier="Mid-Market",
            status="active"
        )
        session.add_all([cust1, cust2, cust3])

        # Seed test orders
        ord1 = Order(
            id="ORD-01",
            customer_id="CUST-001",
            invoice_number="INV-1042",
            amount=149.00,
            status="duplicate_charge",
            transaction_reference="TXN-88102-PRIMARY",
            billing_date=datetime.now(timezone.utc)
        )
        ord2 = Order(
            id="ORD-02",
            customer_id="CUST-001",
            invoice_number="INV-1042",
            amount=149.00,
            status="duplicate_charge",
            transaction_reference="TXN-88103-RETRY",
            billing_date=datetime.now(timezone.utc)
        )
        session.add_all([ord1, ord2])

        # Seed Knowledge Documents
        docs_to_seed = [
            ("doc-billing", "Enterprise Global Billing Policy (2026 Edition)", "billing",
             "Under Section 3 of the Enterprise Agreement, duplicate charges on invoices within 48 hours are eligible for an immediate automatic reversal without managerial re-authorization."),
            ("doc-refund", "Enterprise Refund & Credit Adjustment Policy", "refund",
             "Enterprise customers may request a full refund within 30 days of contract activation or renewal if technical specifications are unmet. Erroneous deductions are 100% refundable immediately."),
            ("doc-sla", "Enterprise Service Level Agreement (SLA) Guidelines", "sla",
             "The platform provides a 99.95% monthly uptime guarantee for Enterprise tier accounts. Initial response for P1 critical outages is within 15 minutes. remedies of 50% service credit apply for uptime below 95%."),
            ("doc-security", "Enterprise Account Security & Verification SOP", "security",
             "Before disclosing invoice records, support engineers must verify customer account number, registered enterprise support PIN, and authorized company email domain.")
        ]

        for d_id, title, cat, content in docs_to_seed:
            doc = KnowledgeDocument(id=d_id, title=title, category=cat, content_hash=f"hash-{d_id}")
            session.add(doc)
            await session.flush()
            chunk = DocumentChunk(
                id=f"{d_id}-C1",
                document_id=d_id,
                chunk_index=1,
                content=content,
                embedding=None
            )
            session.add(chunk)

        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
