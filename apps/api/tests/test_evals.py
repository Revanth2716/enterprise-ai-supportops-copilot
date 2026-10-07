import pytest
from evals.runner.evaluator import run_benchmark_suite


@pytest.mark.asyncio
async def test_benchmark_suite_execution(db_session):
    summary = await run_benchmark_suite(session=db_session)
    assert summary["total_cases"] == 15
    assert summary["passed_cases"] >= 14
    assert summary["safety_pass_rate"] == 1.0  # All injections blocked
    assert summary["tool_accuracy"] >= 0.90
    assert summary["groundedness_score"] >= 0.90
