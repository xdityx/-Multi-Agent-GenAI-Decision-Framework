"""Evaluate deterministic decision consistency for heuristic workflows.

This script checks orchestration stability only. It does not calculate
predictive ML accuracy, precision, recall, ROC, or any production metric.
"""
from __future__ import annotations

import asyncio
import sys
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
    workflow = DecisionWorkflow(
        [
            PaymentDataAgent(tools),
            PaymentRiskAgent(tools),
            PaymentDecisionAgent(tools),
            PaymentExplanationAgent(tools),
        ],
        "evaluation_payments_consistency",
    )
    request = DecisionRequest(
        domain="payments",
        entity_id="CUST_00000",
        context={"customer_id": "CUST_00000", "amount": 2500.0},
    )
    return workflow, request


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
    workflow = DecisionWorkflow(
        [
            ChurnDataAgent(tools),
            ChurnRiskAgent(tools),
            ChurnDecisionAgent(tools),
            ChurnExplanationAgent(tools),
        ],
        "evaluation_churn_consistency",
    )
    request = DecisionRequest(
        domain="churn",
        entity_id="CUST_00000",
        context={"customer_id": "CUST_00000"},
    )
    return workflow, request


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
    workflow = DecisionWorkflow(
        [
            FraudDataAgent(tools),
            FraudRiskAgent(tools),
            FraudDecisionAgent(tools),
            FraudExplanationAgent(tools),
        ],
        "evaluation_fraud_consistency",
    )
    request = DecisionRequest(
        domain="fraud",
        entity_id="TXN_00000000",
        context={"transaction_id": "TXN_00000000"},
    )
    return workflow, request


BUILDERS = {
    "payments": _build_payment_workflow,
    "churn": _build_churn_workflow,
    "fraud": _build_fraud_workflow,
}


async def _evaluate_domain(domain: str, repetitions: int) -> Dict[str, Any]:
    try:
        workflow, request = BUILDERS[domain]()
    except Exception as exc:
        return {"domain": domain, "status": "SKIPPED", "reason": str(exc)}

    observations: List[Dict[str, Any]] = []
    for _ in range(repetitions):
        result = await workflow.execute(request)
        observations.append(
            {
                "decision": result.decision,
                "score": round(float(result.decision_score), 8),
            }
        )

    first = observations[0]
    stable = all(item == first for item in observations)
    return {
        "domain": domain,
        "status": "PASS" if stable else "FAIL",
        "runs": repetitions,
        "decision": first["decision"],
        "score": first["score"],
        "observations": observations,
    }


async def evaluate_decision_consistency(repetitions: int = 3) -> List[Dict[str, Any]]:
    """Run the decision consistency evaluation for all available domains."""
    results = []
    for domain in BUILDERS:
        results.append(await _evaluate_domain(domain, repetitions))
    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    print("\nDecision Consistency")
    print("-" * 60)
    for result in results:
        domain = result["domain"]
        status = result["status"]
        if status == "SKIPPED":
            print(f"{domain:10} {status:7} {result['reason']}")
        else:
            detail = f"decision={result['decision']} score={result['score']} runs={result['runs']}"
            print(f"{domain:10} {status:7} {detail}")


def main() -> List[Dict[str, Any]]:
    results = asyncio.run(evaluate_decision_consistency())
    print_summary(results)
    return results


if __name__ == "__main__":
    main()

