import os
import sys
import json
import asyncio
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select, text

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "apps" / "api"))

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.db.models import User, Customer, Order, KnowledgeDocument, DocumentChunk
from app.rag.chunker import DocumentChunker
from app.rag.embeddings import embedder


async def seed_all():
    print(">>> Starting database seeding for Enterprise AI SupportOps Copilot...")

    base_dir = Path(__file__).resolve().parent

    # 1. Initialize Tables
    async with engine.begin() as conn:
        # Enable pgvector if on postgres
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)
    print("  [+] Database tables verified/created.")

    async with AsyncSessionLocal() as session:
        # 2. Seed Default Support User
        user_stmt = select(User).where(User.email == "support.lead@enterprise.ai")
        u_res = await session.execute(user_stmt)
        if not u_res.scalars().first():
            user = User(
                id="usr-support-01",
                name="Alex Mercer",
                email="support.lead@enterprise.ai",
                role="tier3_support_lead"
            )
            session.add(user)
            print("  [+] Seeded operator user: Alex Mercer")

        # 3. Seed Customers
        with open(base_dir / "customers.json", "r", encoding="utf-8") as f:
            customers_data = json.load(f)

        for c in customers_data:
            stmt = select(Customer).where(Customer.id == c["id"])
            if not (await session.execute(stmt)).scalars().first():
                cust = Customer(
                    id=c["id"],
                    account_number=c["account_number"],
                    name=c["name"],
                    tier=c["tier"],
                    status=c["status"],
                    support_pin=c.get("support_pin"),
                    primary_contact=c.get("primary_contact")
                )
                session.add(cust)
        print(f"  [+] Seeded {len(customers_data)} enterprise customers.")

        # 4. Seed Orders / Invoices
        with open(base_dir / "orders.json", "r", encoding="utf-8") as f:
            orders_data = json.load(f)

        for o in orders_data:
            stmt = select(Order).where(Order.id == o["id"])
            if not (await session.execute(stmt)).scalars().first():
                ord_rec = Order(
                    id=o["id"],
                    customer_id=o["customer_id"],
                    invoice_number=o["invoice_number"],
                    amount=o["amount"],
                    currency=o.get("currency", "USD"),
                    status=o["status"],
                    line_items=o.get("line_items", []),
                    transaction_reference=o.get("transaction_reference"),
                    notes=o.get("notes"),
                    billing_date=datetime.fromisoformat(o["billing_date"].replace("Z", "+00:00"))
                )
                session.add(ord_rec)
        print(f"  [+] Seeded {len(orders_data)} orders & invoice transactions.")

        # 5. Ingest & Chunk Knowledge Base
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
        knowledge_dir = base_dir / "knowledge"

        for md_file in knowledge_dir.glob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            first_line = content.splitlines()[0] if content else ""
            title = first_line.replace("#", "").strip() if first_line.startswith("#") else md_file.stem.replace("_", " ").title()
            category = "billing" if "billing" in md_file.stem else (
                "refund" if "refund" in md_file.stem else (
                    "sla" if "sla" in md_file.stem else "security"
                )
            )
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            doc_id = f"doc-{md_file.stem}"

            stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
            doc_rec = (await session.execute(stmt)).scalars().first()

            if not doc_rec:
                doc_rec = KnowledgeDocument(
                    id=doc_id,
                    title=title,
                    category=category,
                    version="2026.1",
                    content_hash=content_hash
                )
                session.add(doc_rec)
                await session.flush()

                # Chunk document
                chunks = chunker.chunk_markdown(doc_id, title, category, content)

                # Embed chunks if FastEmbed is available
                texts = [ch["content"] for ch in chunks]
                embeddings = embedder.embed_documents(texts) if embedder.is_available else None

                for idx, ch in enumerate(chunks):
                    vec = embeddings[idx] if embeddings else None
                    chunk_rec = DocumentChunk(
                        id=f"{doc_id}-C{idx + 1}",
                        document_id=doc_id,
                        chunk_index=ch["chunk_index"],
                        content=ch["content"],
                        embedding=vec,
                        metadata_=ch["metadata"]
                    )
                    session.add(chunk_rec)
                print(f"  [+] Ingested & indexed {len(chunks)} chunks for: {title}")

        await session.commit()

    print(">>> Seeding completed successfully! Database is ready.\n")


if __name__ == "__main__":
    asyncio.run(seed_all())
