"""Run all local evaluation scripts and print a clean summary."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.evaluate_decision_consistency import (  # noqa: E402
    evaluate_decision_consistency,
    print_summary as print_consistency_summary,
)
from evaluation.evaluate_latency import (  # noqa: E402
    evaluate_latency,
    print_summary as print_latency_summary,
)
from evaluation.evaluate_rag_retrieval import (  # noqa: E402
    evaluate_rag_retrieval,
    print_summary as print_rag_summary,
)
from evaluation.evaluate_trace_completeness import (  # noqa: E402
    evaluate_trace_completeness,
    print_summary as print_trace_summary,
)


def _flatten(groups: Iterable[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    flattened: List[Dict[str, Any]] = []
    for group in groups:
        flattened.extend(group)
    return flattened


def _count_status(results: List[Dict[str, Any]], status: str) -> int:
    return sum(1 for result in results if result.get("status") == status)


async def run_all_evaluations() -> Dict[str, List[Dict[str, Any]]]:
    """Run all local evaluations without live LLM API dependencies."""
    consistency = await evaluate_decision_consistency()
    trace = await evaluate_trace_completeness()
    latency = await evaluate_latency()
    rag = evaluate_rag_retrieval()
    return {
        "decision_consistency": consistency,
        "trace_completeness": trace,
        "latency": latency,
        "rag_retrieval": rag,
    }


def print_summary(results_by_suite: Dict[str, List[Dict[str, Any]]]) -> None:
    print("\nMulti-Agent Decision Framework Evaluations")
    print("=" * 60)
    print("Scope: orchestration consistency, traces, latency, and local RAG sanity")
    print("Note: no predictive ML accuracy metrics or live LLM calls are used.")

    print_consistency_summary(results_by_suite["decision_consistency"])
    print_trace_summary(results_by_suite["trace_completeness"])
    print_latency_summary(results_by_suite["latency"])
    print_rag_summary(results_by_suite["rag_retrieval"])

    all_results = _flatten(results_by_suite.values())
    print("\nOverall Summary")
    print("-" * 60)
    print(f"PASS    {_count_status(all_results, 'PASS')}")
    print(f"FAIL    {_count_status(all_results, 'FAIL')}")
    print(f"SKIPPED {_count_status(all_results, 'SKIPPED')}")


def main() -> Dict[str, List[Dict[str, Any]]]:
    results = asyncio.run(run_all_evaluations())
    print_summary(results)
    return results


if __name__ == "__main__":
    main()

