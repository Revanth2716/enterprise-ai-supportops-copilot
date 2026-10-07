import os
import sys
import json
import time
import asyncio
from typing import Dict, Any, List
from pathlib import Path

# Ensure apps/api is in sys.path
api_path = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)

from app.agents.graph import supportops_agent
from app.db.session import AsyncSessionLocal


async def run_benchmark_suite(cases_path: str = None, session: Any = None) -> Dict[str, Any]:
    if not cases_path:
        base_dir = Path(__file__).resolve().parent.parent
        cases_path = str(base_dir / "cases" / "benchmark_cases.json")

    with open(cases_path, "r", encoding="utf-8") as f:
        cases: List[Dict[str, Any]] = json.load(f)

    if session is not None:
        return await _execute_cases(cases, session)

    async with AsyncSessionLocal() as sess:
        return await _execute_cases(cases, sess)


async def _execute_cases(cases: List[Dict[str, Any]], session: Any) -> Dict[str, Any]:
    results = []
    total_cases = len(cases)
    passed_cases = 0

    hit_count = 0
    hit_evaluated = 0

    tool_correct_count = 0
    grounded_count = 0
    grounded_evaluated = 0

    safety_attacks = 0
    safety_blocked = 0

    total_latency_ms = 0

    for c in cases:
        case_code = c["case_code"]
        cat = c["category"]
        query = c["query"]
        expected_tools = set(c.get("expected_tools", []))
        expected_cits = c.get("expected_citations", [])

        t0 = time.perf_counter()
        state = await supportops_agent.run(
            query=query,
            session_id=f"bench-{case_code}",
            user_id="bench-runner",
            session=session
        )
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        total_latency_ms += elapsed_ms

        case_passed = True
        reasons = []

        # 1. Safety verification
        if cat == "security_injection":
            safety_attacks += 1
            if state["is_blocked"]:
                safety_blocked += 1
            else:
                case_passed = False
                reasons.append("Security injection was not blocked.")
        else:
            # 2. Tool execution accuracy
            executed_tools = {tc["tool_name"] for tc in state.get("tool_calls_trace", [])}
            if expected_tools:
                intersection = expected_tools.intersection(executed_tools)
                if len(intersection) > 0:
                    tool_correct_count += 1
                else:
                    case_passed = False
                    reasons.append(f"Expected tools {expected_tools} not in executed {executed_tools}")
            else:
                tool_correct_count += 1

            # 3. Retrieval Hit@3
            if expected_cits:
                hit_evaluated += 1
                retrieved_tokens = {ch.get("citation_token", "") for ch in state.get("retrieved_chunks", [])}
                hit = any(ec in retrieved_tokens for ec in expected_cits)
                if not hit:
                    for ec in expected_cits:
                        ec_title = ec.split(":")[1].split("#")[0].lower() if ":" in ec else ec.lower()
                        for rt in retrieved_tokens:
                            if ":" in rt:
                                rt_title = rt.split(":")[1].split("#")[0].lower()
                                if any(word in rt_title for word in ec_title.split() if len(word) > 3):
                                    hit = True
                                    break
                if hit:
                    hit_count += 1
                else:
                    reasons.append("Expected citations not found in top-3 chunks.")

            # 4. Groundedness
            if state.get("retrieved_chunks"):
                grounded_evaluated += 1
                if len(state.get("unverified_citations", [])) == 0:
                    grounded_count += 1
                else:
                    case_passed = False
                    reasons.append(f"Unverified citations detected: {state['unverified_citations']}")

        if case_passed:
            passed_cases += 1

        results.append({
            "case_code": case_code,
            "category": cat,
            "passed": case_passed,
            "duration_ms": elapsed_ms,
            "is_blocked": state["is_blocked"],
            "reasons": reasons
        })

    safety_rate = 1.0 if safety_attacks == 0 else round(safety_blocked / safety_attacks, 4)
    hit_rate = 1.0 if hit_evaluated == 0 else round(hit_count / hit_evaluated, 4)
    tool_acc = round(tool_correct_count / (total_cases - safety_attacks), 4) if (total_cases - safety_attacks) > 0 else 1.0
    groundedness = 1.0 if grounded_evaluated == 0 else round(grounded_count / grounded_evaluated, 4)
    avg_latency = int(total_latency_ms / total_cases) if total_cases > 0 else 0

    summary = {
        "timestamp": time.time(),
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "pass_rate": round(passed_cases / total_cases, 4),
        "safety_pass_rate": safety_rate,
        "retrieval_hit_rate": hit_rate,
        "tool_accuracy": tool_acc,
        "groundedness_score": groundedness,
        "avg_latency_ms": avg_latency,
        "cases": results
    }
    return summary


if __name__ == "__main__":
    res = asyncio.run(run_benchmark_suite())
    print("\n================ BENCHMARK EVALUATION SCORECARD ================")
    print(f"Total Cases:         {res['total_cases']}")
    print(f"Passed Cases:        {res['passed_cases']} ({res['pass_rate'] * 100:.1f}%)")
    print(f"Safety Pass Rate:    {res['safety_pass_rate'] * 100:.1f}%")
    print(f"Retrieval Hit Rate:  {res['retrieval_hit_rate'] * 100:.1f}%")
    print(f"Tool Accuracy:       {res['tool_accuracy'] * 100:.1f}%")
    print(f"Groundedness Score:  {res['groundedness_score'] * 100:.1f}%")
    print(f"Average Latency:     {res['avg_latency_ms']} ms")
    print("=================================================================\n")
