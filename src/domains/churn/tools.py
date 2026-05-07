"""Churn-specific tools for agents."""
import random
from typing import Any, Dict, List

from .data import Customer, get_customer_profile, get_engagement_trends


class ChurnTools:
    """Tools for churn prediction and customer retention agents."""

    def __init__(self, customers: List[Customer]) -> None:
        self.customers = customers

    def get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer profile by ID."""
        return get_customer_profile(customer_id, self.customers)

    def get_engagement_analysis(self, customer_id: str) -> Dict[str, Any]:
        """Derive engagement trend labels for a customer."""
        return get_engagement_trends(customer_id, self.customers)

    def calculate_churn_score(self, customer_id: str) -> Dict[str, Any]:
        """
        Calculate churn probability score (0-100).

        Lower score = lower churn risk. Uses a heuristic model based on
        engagement signals; a production system would use an ML model.
        """
        profile = self.get_customer_data(customer_id)

        if "error" in profile:
            return {"churn_score": 50, "reasoning": "Customer not found — defaulting to medium risk"}

        score = 50  # Baseline

        # Healthy signals reduce risk
        if profile["login_frequency"] >= 5:
            score -= 15
        if profile["feature_adoption"] > 0.7:
            score -= 15
        if profile["nps_score"] >= 50:
            score -= 20
        if profile["is_vip"]:
            score -= 10

        # Risky signals increase risk
        if profile["login_frequency"] < 2:
            score += 25
        if profile["feature_adoption"] < 0.5:
            score += 20
        if profile["nps_score"] < 30:
            score += 25
        if profile["last_login_days_ago"] > 30:
            score += 15
        if profile["support_tickets"] > 10:
            score += 15

        return {
            "churn_score": max(0, min(100, score)),
            "reasoning": "Based on engagement, NPS, usage patterns, and inactivity",
        }

    def calculate_customer_value(self, customer_id: str) -> Dict[str, Any]:
        """Calculate LTV and maximum retention budget for a customer."""
        profile = self.get_customer_data(customer_id)

        if "error" in profile:
            return {"ltv": 0, "tier": "Unknown", "retention_budget": 0, "cac_multiplier": 5}

        ltv = profile["ltv_amount"]

        if ltv > 50_000:
            tier = "VIP"
            retention_budget = ltv * 0.20
        elif ltv > 5_000:
            tier = "Standard"
            retention_budget = ltv * 0.10
        else:
            tier = "Basic"
            retention_budget = ltv * 0.05

        return {
            "ltv": ltv,
            "tier": tier,
            "retention_budget": round(retention_budget, 2),
            "cac_multiplier": 5 + random.uniform(0, 20),  # CAC is 5-25x retention cost
        }

    def determine_retention_action(
        self, churn_score: float, ltv_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map churn score + customer tier to a retention action."""
        if churn_score > 70:
            if ltv_data.get("tier") == "VIP":
                action = "EXECUTIVE_OUTREACH"
                desc = "Immediate executive engagement for high-value at-risk customer"
            else:
                action = "URGENT_RETENTION"
                desc = "Immediate retention call + discount offer"
        elif churn_score > 40:
            action = "PROACTIVE_OUTREACH"
            desc = "Personalised email + feature tips + community engagement"
        else:
            action = "STANDARD_ENGAGEMENT"
            desc = "Continue standard engagement cadence"

        return {
            "recommended_action": action,
            "description": desc,
            "urgency": (
                "HIGH" if churn_score > 70 else "MEDIUM" if churn_score > 40 else "LOW"
            ),
        }


def create_tools(customers: List[Customer]) -> ChurnTools:
    """Factory function to create a configured ChurnTools instance."""
    return ChurnTools(customers)
