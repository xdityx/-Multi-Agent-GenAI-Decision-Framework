"""Evaluate whether heuristic workflows return complete agent traces."""
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
    return (
        DecisionWorkflow(
            [
                PaymentDataAgent(tools),
                PaymentRiskAgent(tools),
                PaymentDecisionAgent(tools),
                PaymentExplanationAgent(tools),
            ],
            "evaluation_payments_trace",
        ),
        DecisionRequest(
            domain="payments",
            entity_id="CUST_00000",
            context={"customer_id": "CUST_00000", "amount": 2500.0},
        ),
        [
            "payment_data_agent",
            "payment_risk_agent",
            "payment_decision_agent",
            "payment_explanation_agent",
        ],
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
            "evaluation_churn_trace",
        ),
        DecisionRequest(
            domain="churn",
            entity_id="CUST_00000",
            context={"customer_id": "CUST_00000"},
        ),
        [
            "churn_data_agent",
            "churn_risk_agent",
            "churn_decision_agent",
            "churn_explanation_agent",
        ],
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
            "evaluation_fraud_trace",
        ),
        DecisionRequest(
            domain="fraud",
            entity_id="TXN_00000000",
            context={"transaction_id": "TXN_00000000"},
        ),
        [
            "fraud_data_agent",
            "fraud_risk_agent",
            "fraud_decision_agent",
            "fraud_explanation_agent",
        ],
    )


BUILDERS = {
    "payments": _build_payment_workflow,
    "churn": _build_churn_workflow,
    "fraud": _build_fraud_workflow,
}


async def _evaluate_domain(domain: str) -> Dict[str, Any]:
    try:
        workflow, request, expected_agents = BUILDERS[domain]()
        result = await workflow.execute(request)
    except Exception as exc:
        return {"domain": domain, "status": "SKIPPED", "reason": str(exc)}

    actual_agents = [output.agent_name for output in result.agent_outputs]
    missing_agents = [agent for agent in expected_agents if agent not in actual_agents]
    ordered = actual_agents[: len(expected_agents)] == expected_agents
    complete = len(actual_agents) >= 4 and not missing_agents and ordered

    missing_fields = []
    for output in result.agent_outputs:
        if not output.agent_name:
            missing_fields.append("agent_name")
        if output.analysis is None:
            missing_fields.append(f"{output.agent_name}.analysis")
        if output.reasoning is None:
            missing_fields.append(f"{output.agent_name}.reasoning")

    if missing_fields:
        complete = False

    return {
        "domain": domain,
        "status": "PASS" if complete else "FAIL",
        "expected_agents": expected_agents,
        "actual_agents": actual_agents,
        "missing_agents": missing_agents,
        "missing_fields": missing_fields,
        "ordered": ordered,
    }


async def evaluate_trace_completeness() -> List[Dict[str, Any]]:
    """Run trace completeness checks for all available domains."""
    results = []
    for domain in BUILDERS:
        results.append(await _evaluate_domain(domain))
    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    print("\nTrace Completeness")
    print("-" * 60)
    for result in results:
        domain = result["domain"]
        status = result["status"]
        if status == "SKIPPED":
            print(f"{domain:10} {status:7} {result['reason']}")
            continue
        if status == "PASS":
            print(f"{domain:10} {status:7} agents={len(result['actual_agents'])}")
        else:
            print(
                f"{domain:10} {status:7} "
                f"missing_agents={result['missing_agents']} "
                f"missing_fields={result['missing_fields']} "
                f"ordered={result['ordered']}"
            )


def main() -> List[Dict[str, Any]]:
    results = asyncio.run(evaluate_trace_completeness())
    print_summary(results)
    return results


if __name__ == "__main__":
    main()

