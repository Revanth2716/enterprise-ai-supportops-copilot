import json
import sys
import asyncio
from typing import Dict, Any

# Standalone lightweight MCP server implementing JSON-RPC 2.0 protocol
TOOLS_METADATA = [
    {
        "name": "search_knowledge",
        "description": "Searches enterprise policies using hybrid vector and lexical retrieval.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query keywords"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_customer",
        "description": "Looks up customer enterprise tier and status in CRM.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_identifier": {"type": "string", "description": "Customer name or account ID"}
            },
            "required": ["customer_identifier"]
        }
    },
    {
        "name": "get_order_history",
        "description": "Retrieves orders and detects duplicate charge anomalies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Customer ID (e.g. CUST-001)"},
                "invoice_number": {"type": "string", "description": "Invoice number (e.g. INV-1042)"}
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "lookup_policy",
        "description": "Fetches verified enterprise policy excerpts by category.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "billing, refund, or sla"}
            },
            "required": ["category"]
        }
    }
]


def handle_rpc_request(req: Dict[str, Any]) -> Dict[str, Any]:
    method = req.get("method")
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_METADATA}
        }
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})

        # Return mock protocol execution result
        result_content = {
            "mcp_executed": True,
            "tool": name,
            "arguments": args,
            "status": "success",
            "message": f"Tool '{name}' processed via MCP protocol successfully."
        }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result_content)}]}
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"}
        }


async def main():
    """Reads JSON-RPC from stdin and writes responses to stdout."""
    for line in sys.stdin:
        line_clean = line.strip()
        if not line_clean:
            continue
        try:
            req = json.loads(line_clean)
            resp = handle_rpc_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
