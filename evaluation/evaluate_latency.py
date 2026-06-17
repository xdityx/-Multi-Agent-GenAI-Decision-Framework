"""Measure simple local workflow latency for heuristic requests."""
from __future__ import annotations

import asyncio
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _build_payment_workflow():
    from src.core.schemas import DecisionRequest
    from src.core.workflow import DecisionWorkflow
    from src.domains.payments.agents import (
        PaymentDataAgent,
        PaymentDecisionAgent,
        PaymentExplanationAgent,
        PaymentRiskAgent,
    )
    from src.domains.payments.data import PaymentDataGenerator
    from src.domains.payments.tools import create_tools

    generator = PaymentDataGenerator(seed=42)
    customers = generator.generate_customers(count=50)
    transactions = generator.generate_transactions(customers, count=100)
    tools = create_tools(customers, transactions)
    return (
        DecisionWorkflow(
            [
                PaymentDataAgent(tools),
                PaymentRiskAgent(tools),
                PaymentDecisionAgent(tools),
                PaymentExplanationAgent(tools),
            ],
            "evaluation_payments_latency",
        ),
        DecisionRequest(
            domain="payments",
            entity_id="CUST_00000",
            context={"customer_id": "CUST_00000", "amount": 2500.0},
        ),
    )


def _build_churn_workflow():
    from src.core.schemas import DecisionRequest
    from src.core.workflow import DecisionWorkflow
    from src.domains.churn.agents import (
        ChurnDataAgent,
        ChurnDecisionAgent,
        ChurnExplanationAgent,
        ChurnRiskAgent,
    )
    from src.domains.churn.data import ChurnDataGenerator
    from src.domains.churn.tools import create_tools

    customers = ChurnDataGenerator(seed=42).generate_customers(count=50)
    tools = create_tools(customers)
    return (
        DecisionWorkflow(
            [
                ChurnDataAgent(tools),
                ChurnRiskAgent(tools),
                ChurnDecisionAgent(tools),
                ChurnExplanationAgent(tools),
            ],
            "evaluation_churn_latency",
        ),
        DecisionRequest(
            domain="churn",
            entity_id="CUST_00000",
            context={"customer_id": "CUST_00000"},
        ),
    )


def _build_fraud_workflow():
    from src.core.schemas import DecisionRequest
    from src.core.workflow import DecisionWorkflow
    from src.domains.fraud.agents import (
        FraudDataAgent,
        FraudDecisionAgent,
        FraudExplanationAgent,
        FraudRiskAgent,
    )
    from src.domains.fraud.data import FraudDataGenerator
    from src.domains.fraud.tools import create_tools

    transactions = FraudDataGenerator(seed=42).generate_transactions(count=100)
    tools = create_tools(transactions)
    return (
        DecisionWorkflow(
            [
                FraudDataAgent(tools),
                FraudRiskAgent(tools),
                FraudDecisionAgent(tools),
                FraudExplanationAgent(tools),
            ],
            "evaluation_fraud_latency",
        ),
        DecisionRequest(
            domain="fraud",
            entity_id="TXN_00000000",
            context={"transaction_id": "TXN_00000000"},
        ),
    )


BUILDERS = {
    "payments": _build_payment_workflow,
    "churn": _build_churn_workflow,
    "fraud": _build_fraud_workflow,
}


async def _evaluate_domain(domain: str, sample_size: int) -> Dict[str, Any]:
    try:
        workflow, request = BUILDERS[domain]()
    except Exception as exc:
        return {"domain": domain, "status": "SKIPPED", "reason": str(exc)}

    latencies_ms = []
    for _ in range(sample_size):
        start = time.perf_counter()
        await workflow.execute(request)
        latencies_ms.append((time.perf_counter() - start) * 1000.0)

    return {
        "domain": domain,
        "status": "PASS",
        "runs": sample_size,
        "avg_ms": round(statistics.mean(latencies_ms), 3),
        "min_ms": round(min(latencies_ms), 3),
        "max_ms": round(max(latencies_ms), 3),
    }


async def evaluate_latency(sample_size: int = 5) -> List[Dict[str, Any]]:
    """Measure latency for all available heuristic workflows."""
    results = []
    for domain in BUILDERS:
        results.append(await _evaluate_domain(domain, sample_size))
    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    print("\nLatency")
    print("-" * 60)
    for result in results:
        domain = result["domain"]
        status = result["status"]
        if status == "SKIPPED":
            print(f"{domain:10} {status:7} {result['reason']}")
        else:
            print(
                f"{domain:10} {status:7} "
                f"avg={result['avg_ms']}ms min={result['min_ms']}ms "
                f"max={result['max_ms']}ms runs={result['runs']}"
            )


def main() -> List[Dict[str, Any]]:
    results = asyncio.run(evaluate_latency())
    print_summary(results)
    return results


if __name__ == "__main__":
    main()

