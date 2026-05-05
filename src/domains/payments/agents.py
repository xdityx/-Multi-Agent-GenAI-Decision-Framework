"""Payment-specific agents that inherit from core Agent."""
from typing import Any, Dict

from src.core.agent import Agent
from src.core.schemas import AgentOutput

from .tools import PaymentTools


class PaymentDataAgent(Agent):
    """Agent responsible for gathering payment context."""

    def __init__(self, tools: PaymentTools) -> None:
        super().__init__(
            name="payment_data_agent",
            responsibility="Gather customer and transaction context",
        )
        self.payment_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Gather customer profile and transaction history."""
        customer_id = context.get("customer_id", "CUST_00001")
        amount = context.get("amount", 1000)

        customer_profile = self.payment_tools.get_customer_profile(customer_id)
        transaction_history = self.payment_tools.get_transaction_history(customer_id)

        analysis = {
            "customer_profile": customer_profile,
            "transaction_history": transaction_history,
            "current_transaction": {"amount": amount},
        }

        reasoning = (
            f"Gathered data for customer {customer_id}, "
            f"transaction amount ${amount}"
        )

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=["get_customer_profile", "get_transaction_history"],
            reasoning=reasoning,
        )


class PaymentRiskAgent(Agent):
    """Agent responsible for fraud and payment risk analysis."""

    def __init__(self, tools: PaymentTools) -> None:
        super().__init__(
            name="payment_risk_agent",
            responsibility="Analyze fraud and payment risk",
        )
        self.payment_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Run fraud score, velocity, and sanctions checks."""
        customer_id = context.get("customer_id", "CUST_00001")
        amount = context.get("amount", 1000)

        fraud_score_result = self.payment_tools.calculate_fraud_score(
            customer_id, amount
        )
        velocity_result = self.payment_tools.check_velocity(customer_id, amount)
        sanctions_result = self.payment_tools.check_sanctions(customer_id)

        analysis: Dict[str, Any] = {
            "fraud_score": fraud_score_result["fraud_score"],
            "velocity_check": velocity_result,
            "sanctions_check": sanctions_result,
        }

        reasoning = (
            f"Fraud score: {fraud_score_result['fraud_score']}, "
            f"Velocity: {'OK' if velocity_result['velocity_ok'] else 'HIGH'}, "
            f"Sanctions: {sanctions_result['status']}"
        )

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=["calculate_fraud_score", "check_velocity", "check_sanctions"],
            reasoning=reasoning,
        )


class PaymentDecisionAgent(Agent):
    """Agent responsible for the final approval decision."""

    def __init__(self, tools: PaymentTools) -> None:
        super().__init__(
            name="payment_decision_agent",
            responsibility="Make approval / decline / review decision",
        )
        self.payment_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Apply business rules to derive APPROVE / DECLINE / REVIEW."""
        # Consume risk analysis produced by the previous agent
        risk_analysis = context.get("previous_agent_output", {})
        fraud_score: float = risk_analysis.get("fraud_score", 50)
        velocity_result: Dict[str, Any] = risk_analysis.get("velocity_check", {})

        decision_result = self.payment_tools.apply_business_rules(
            fraud_score=fraud_score,
            velocity_ok=velocity_result.get("velocity_ok", True),
        )

        # Convert fraud score to a 0-1 confidence: lower fraud → higher confidence
        confidence = max(0.0, 100.0 - fraud_score) / 100.0

        analysis: Dict[str, Any] = {
            "decision": decision_result["decision"],
            "score": confidence,
            "reason": decision_result["reason"],
        }

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=["apply_business_rules"],
            reasoning=decision_result["reason"],
        )


class PaymentExplanationAgent(Agent):
    """Agent responsible for generating human-readable decision explanations."""

    def __init__(self, tools: PaymentTools) -> None:
        super().__init__(
            name="payment_explanation_agent",
            responsibility="Generate clear explanations for decisions",
        )
        self.payment_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Produce a plain-language explanation of the decision."""
        decision_analysis = context.get("previous_agent_output", {})
        decision = decision_analysis.get("decision", "PENDING")
        reason = decision_analysis.get("reason", "No reason provided")
        confidence = decision_analysis.get("score", 0.5)

        explanation = (
            f"PAYMENT DECISION: {decision}\n\n"
            f"Reason: {reason}\n\n"
            "This decision was made based on:\n"
            "  1. Customer fraud history and profile\n"
            "  2. Transaction amount compared to customer's typical spending\n"
            "  3. Account velocity and transaction limits\n"
            "  4. Sanctions screening\n\n"
            f"The decision carries {confidence:.0%} confidence."
        )

        analysis: Dict[str, Any] = {
            "decision": decision,
            "explanation": explanation,
        }

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=[],
            reasoning="Generated clear explanation for end user",
        )
