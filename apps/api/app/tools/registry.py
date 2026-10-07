import asyncio
import time
import logging
from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.calculator import safe_calculate
from app.tools.customer_tools import get_customer
from app.tools.order_tools import get_order_history
from app.tools.policy_tools import lookup_policy
from app.tools.ticket_tools import draft_ticket
from app.rag.retriever import hybrid_retriever

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    tool_name: str
    source: str = "local"
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int = 0


class ToolRegistry:
    """
    Central registry for safe, deterministic enterprise tools.
    Never allows arbitrary SQL or code execution.
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register(self, name: str, description: str, handler: Callable, permission: str = "READ_ONLY"):
        self._tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "permission": permission
        }

    def list_tools(self) -> List[Dict[str, str]]:
        return [
            {"name": k, "description": v["description"], "permission": v["permission"]}
            for k, v in self._tools.items()
        ]

    def _register_default_tools(self):
        self.register(
            name="search_knowledge",
            description="Searches enterprise billing, refund, and SLA policies using hybrid RAG.",
            handler=self._handle_search_knowledge
        )
        self.register(
            name="get_customer",
            description="Looks up customer enterprise tier, status, and account ID by name or account number.",
            handler=self._handle_get_customer
        )
        self.register(
            name="get_order_history",
            description="Retrieves customer orders and checks for duplicate charges or invoice discrepancies.",
            handler=self._handle_get_order_history
        )
        self.register(
            name="lookup_policy",
            description="Direct lookup of enterprise policies by category (billing, refund, sla, security).",
            handler=self._handle_lookup_policy
        )
        self.register(
            name="calculate",
            description="Safely computes arithmetic expressions (e.g. 149 * 2 - 149) using a restricted AST evaluator.",
            handler=self._handle_calculate
        )
        self.register(
            name="draft_ticket",
            description="Prepares a structured support resolution draft ticket for operator review.",
            handler=self._handle_draft_ticket,
            permission="OPERATOR_ACTION"
        )

    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        session: Optional[AsyncSession] = None,
        source: str = "local"
    ) -> ToolResult:
        if tool_name not in self._tools:
            return ToolResult(
                tool_name=tool_name,
                source=source,
                success=False,
                error=f"Tool '{tool_name}' is not in authorized tool registry."
            )

        start_time = time.perf_counter()
        tool = self._tools[tool_name]

        try:
            handler = tool["handler"]
            # Time-bounded execution
            res = await asyncio.wait_for(handler(parameters, session), timeout=5.0)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            return ToolResult(
                tool_name=tool_name,
                source=source,
                success=True,
                data=res,
                duration_ms=elapsed_ms
            )
        except asyncio.TimeoutError:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                tool_name=tool_name,
                source=source,
                success=False,
                error=f"Tool '{tool_name}' timed out after 5.0 seconds.",
                duration_ms=elapsed_ms
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error("tool_execution_failed", extra={"tool": tool_name, "error": str(e)})
            return ToolResult(
                tool_name=tool_name,
                source=source,
                success=False,
                error=f"Execution error: {str(e)}",
                duration_ms=elapsed_ms
            )

    # Handlers
    async def _handle_search_knowledge(self, params: dict, session: Optional[AsyncSession]) -> dict:
        query = params.get("query", "")
        top_k = params.get("top_k", 3)
        if not session:
            return {"error": "Database session required for search_knowledge."}
        return await hybrid_retriever.search(query, session, top_k=top_k)

    async def _handle_get_customer(self, params: dict, session: Optional[AsyncSession]) -> dict:
        identifier = params.get("customer_identifier") or params.get("name") or params.get("account_number") or ""
        if not session:
            return {"error": "Database session required for get_customer."}
        return await get_customer(identifier, session)

    async def _handle_get_order_history(self, params: dict, session: Optional[AsyncSession]) -> dict:
        customer_id = params.get("customer_id", "")
        invoice_number = params.get("invoice_number")
        if not session:
            return {"error": "Database session required for get_order_history."}
        return await get_order_history(customer_id, invoice_number, session)

    async def _handle_lookup_policy(self, params: dict, session: Optional[AsyncSession]) -> dict:
        category = params.get("category") or params.get("policy_category") or "billing"
        if not session:
            return {"error": "Database session required for lookup_policy."}
        return await lookup_policy(category, session)

    async def _handle_calculate(self, params: dict, session: Optional[AsyncSession]) -> dict:
        expr = params.get("expression", "")
        return safe_calculate(expr)

    async def _handle_draft_ticket(self, params: dict, session: Optional[AsyncSession]) -> dict:
        customer_id = params.get("customer_id", "UNKNOWN")
        title = params.get("title", "Support Resolution")
        priority = params.get("priority", "P3_NORMAL")
        body = params.get("body", "")
        reversal = float(params.get("reversal_amount", 0.0))
        invoice = params.get("invoice_number", "")
        return draft_ticket(customer_id, title, priority, body, reversal, invoice)


# Global registry singleton
tool_registry = ToolRegistry()
