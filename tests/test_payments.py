"""Tests for the payments domain."""
import pytest
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


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def payment_data():
    """Generate deterministic payment data for testing (seed=42)."""
    generator = PaymentDataGenerator(seed=42)
    customers = generator.generate_customers(count=50)
    transactions = generator.generate_transactions(customers, count=100)
    return customers, transactions


# ---------------------------------------------------------------------------
# Data generation tests
# ---------------------------------------------------------------------------


def test_payment_data_generation(payment_data):
    """Data generator produces the correct number of records."""
    customers, transactions = payment_data
    assert len(customers) == 50
    assert len(transactions) == 100
    assert customers[0].customer_id == "CUST_00000"


def test_customer_ids_are_unique(payment_data):
    """Each generated customer has a unique ID."""
    customers, _ = payment_data
    ids = [c.customer_id for c in customers]
    assert len(ids) == len(set(ids))


def test_transaction_ids_are_unique(payment_data):
    """Each generated transaction has a unique ID."""
    _, transactions = payment_data
    ids = [t.transaction_id for t in transactions]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Tool tests
# ---------------------------------------------------------------------------


def test_payment_tools_profile(payment_data):
    """get_customer_profile returns correct customer data."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    profile = tools.get_customer_profile("CUST_00000")
    assert profile["customer_id"] == "CUST_00000"
    assert "account_age_years" in profile
    assert "fraud_history" in profile


def test_payment_tools_fraud_score(payment_data):
    """calculate_fraud_score returns a score clamped to [0, 100]."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    result = tools.calculate_fraud_score("CUST_00000", 1000)
    assert 0 <= result["fraud_score"] <= 100
    assert "reasoning" in result


def test_payment_tools_velocity(payment_data):
    """check_velocity flags amounts that exceed 50 % of the account limit."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    # Use an amount that is definitely within limit (e.g. $1)
    low_result = tools.check_velocity("CUST_00000", 1.0)
    assert low_result["velocity_ok"] is True
    assert low_result["risk"] == "low"

    # Use an amount that exceeds every possible account limit
    high_result = tools.check_velocity("CUST_00000", 999_999.0)
    assert high_result["velocity_ok"] is False
    assert high_result["risk"] == "high"


def test_payment_tools_unknown_customer(payment_data):
    """Tools return an error dict for an unknown customer ID."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    profile = tools.get_customer_profile("CUST_XXXXX")
    assert "error" in profile


def test_business_rules_approve(payment_data):
    """Low fraud score + good velocity → APPROVE."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    result = tools.apply_business_rules(fraud_score=10, velocity_ok=True)
    assert result["decision"] == "APPROVE"


def test_business_rules_review(payment_data):
    """Medium fraud score + good velocity → REVIEW."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    result = tools.apply_business_rules(fraud_score=50, velocity_ok=True)
    assert result["decision"] == "REVIEW"


def test_business_rules_decline_high_score(payment_data):
    """High fraud score → DECLINE."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    result = tools.apply_business_rules(fraud_score=80, velocity_ok=True)
    assert result["decision"] == "DECLINE"


def test_business_rules_decline_velocity(payment_data):
    """Velocity violation → DECLINE regardless of fraud score."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    result = tools.apply_business_rules(fraud_score=5, velocity_ok=False)
    assert result["decision"] == "DECLINE"


# ---------------------------------------------------------------------------
# Agent tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_payment_data_agent(payment_data):
    """PaymentDataAgent populates customer_profile and transaction_history."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)
    agent = PaymentDataAgent(tools)

    output = await agent.run({"customer_id": "CUST_00000", "amount": 1500})

    assert output.agent_name == "payment_data_agent"
    assert "customer_profile" in output.analysis
    assert "transaction_history" in output.analysis


@pytest.mark.asyncio
async def test_payment_risk_agent(payment_data):
    """PaymentRiskAgent produces fraud_score, velocity_check, sanctions_check."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)
    agent = PaymentRiskAgent(tools)

    output = await agent.run({"customer_id": "CUST_00000", "amount": 1500})

    assert output.agent_name == "payment_risk_agent"
    assert "fraud_score" in output.analysis
    assert "velocity_check" in output.analysis
    assert "sanctions_check" in output.analysis


@pytest.mark.asyncio
async def test_payment_decision_agent(payment_data):
    """PaymentDecisionAgent maps risk output to APPROVE / DECLINE / REVIEW."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)
    agent = PaymentDecisionAgent(tools)

    context = {
        "customer_id": "CUST_00000",
        "amount": 1500,
        "previous_agent_output": {
            "fraud_score": 30,
            "velocity_check": {"velocity_ok": True},
        },
    }
    output = await agent.run(context)

    assert output.agent_name == "payment_decision_agent"
    assert output.analysis["decision"] in {"APPROVE", "DECLINE", "REVIEW"}
    assert 0.0 <= output.analysis["score"] <= 1.0


@pytest.mark.asyncio
async def test_payment_explanation_agent(payment_data):
    """PaymentExplanationAgent produces a human-readable explanation."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)
    agent = PaymentExplanationAgent(tools)

    context = {
        "previous_agent_output": {
            "decision": "APPROVE",
            "reason": "Low risk, auto-approved",
            "score": 0.9,
        }
    }
    output = await agent.run(context)

    assert output.agent_name == "payment_explanation_agent"
    assert "APPROVE" in output.analysis["explanation"]
    assert "explanation" in output.analysis


# ---------------------------------------------------------------------------
# Full workflow test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_payment_workflow_end_to_end(payment_data):
    """Full 4-agent payment workflow produces a valid DecisionResult."""
    customers, transactions = payment_data
    tools = create_tools(customers, transactions)

    agents = [
        PaymentDataAgent(tools),
        PaymentRiskAgent(tools),
        PaymentDecisionAgent(tools),
        PaymentExplanationAgent(tools),
    ]

    workflow = DecisionWorkflow(agents, "payment_workflow")

    request = DecisionRequest(
        domain="payments",
        entity_id="CUST_00000",
        context={"customer_id": "CUST_00000", "amount": 2500},
    )

    result = await workflow.execute(request)

    assert result.domain == "payments"
    assert len(result.agent_outputs) == 4
    assert result.decision in {"APPROVE", "DECLINE", "REVIEW"}
    assert 0.0 <= result.decision_score <= 1.0
