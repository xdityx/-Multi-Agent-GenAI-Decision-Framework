"""Churn domain heuristic agents — inherit from core Agent."""
from typing import Any, Dict

from src.core.agent import Agent
from src.core.schemas import AgentOutput

from .tools import ChurnTools


class ChurnDataAgent(Agent):
    """Agent that gathers customer engagement data."""

    def __init__(self, tools: ChurnTools) -> None:
        super().__init__(
            name="churn_data_agent",
            responsibility="Gather customer profile and engagement data",
        )
        self.churn_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Collect customer profile and engagement trends."""
        customer_id = context.get("customer_id", "CUST_00001")

        customer_profile = self.churn_tools.get_customer_data(customer_id)
        engagement = self.churn_tools.get_engagement_analysis(customer_id)

        analysis: Dict[str, Any] = {
            "customer_profile": customer_profile,
            "engagement_trends": engagement,
        }

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=["get_customer_data", "get_engagement_analysis"],
            reasoning=f"Gathered engagement data for customer {customer_id}",
        )


class ChurnRiskAgent(Agent):
    """Agent that scores churn risk and evaluates customer value."""

    def __init__(self, tools: ChurnTools) -> None:
        super().__init__(
            name="churn_risk_agent",
            responsibility="Analyze churn risk and customer lifetime value",
        )
        self.churn_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Calculate churn score and LTV tier."""
        customer_id = context.get("customer_id", "CUST_00001")

        churn_result = self.churn_tools.calculate_churn_score(customer_id)
        ltv_result = self.churn_tools.calculate_customer_value(customer_id)

        churn_score = churn_result["churn_score"]
        churn_category = (
            "HIGH" if churn_score > 70 else "MEDIUM" if churn_score > 40 else "LOW"
        )

        analysis: Dict[str, Any] = {
            "churn_score": churn_score,
            "churn_category": churn_category,
            "ltv": ltv_result["ltv"],
            "customer_tier": ltv_result["tier"],
            "retention_budget": ltv_result["retention_budget"],
        }

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=["calculate_churn_score", "calculate_customer_value"],
            reasoning=(
                f"Churn score: {churn_score} ({churn_category}), "
                f"Tier: {ltv_result['tier']}, LTV: ${ltv_result['ltv']:.0f}"
            ),
        )


class ChurnDecisionAgent(Agent):
    """Agent that maps risk + value to a retention action."""

    def __init__(self, tools: ChurnTools) -> None:
        super().__init__(
            name="churn_decision_agent",
            responsibility="Determine the appropriate retention strategy",
        )
        self.churn_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Select a retention action based on churn score and LTV."""
        risk = context.get("previous_agent_output", {})
        churn_score: float = risk.get("churn_score", 50)
        ltv_data: Dict[str, Any] = {
            "ltv": risk.get("ltv", 5000),
            "tier": risk.get("customer_tier", "Standard"),
            "retention_budget": risk.get("retention_budget", 500),
        }

        retention = self.churn_tools.determine_retention_action(churn_score, ltv_data)

        # Convert churn score → confidence: lower churn = higher confidence in keeping
        confidence = max(0.0, 100.0 - churn_score) / 100.0

        analysis: Dict[str, Any] = {
            "decision": retention["recommended_action"],
            "urgency": retention["urgency"],
            "score": confidence,
        }

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=["determine_retention_action"],
            reasoning=retention["description"],
        )


class ChurnExplanationAgent(Agent):
    """Agent that generates plain-English retention explanations."""

    def __init__(self, tools: ChurnTools) -> None:
        super().__init__(
            name="churn_explanation_agent",
            responsibility="Generate clear retention strategy explanations",
        )
        self.churn_tools = tools

    async def run(self, context: Dict[str, Any]) -> AgentOutput:
        """Produce a human-readable explanation of the retention decision."""
        prev = context.get("previous_agent_output", {})
        decision = prev.get("decision", "STANDARD_ENGAGEMENT")
        urgency = prev.get("urgency", "LOW")
        confidence = prev.get("score", 0.5)

        explanation = (
            f"RETENTION STRATEGY: {decision}\n\n"
            "Based on our analysis:\n"
            "  1. We identified engagement decline signals in this customer's activity.\n"
            f"  2. Urgency level is {urgency} — action recommended accordingly.\n"
            f"  3. We are {confidence:.0%} confident this customer can be retained.\n\n"
            "Our team will reach out with targeted retention offers."
        )

        analysis: Dict[str, Any] = {
            "decision": decision,
            "explanation": explanation,
        }

        return AgentOutput(
            agent_name=self.name,
            analysis=analysis,
            tools_used=[],
            reasoning="Generated plain-English retention explanation",
        )
