"""Payment-specific tools for agents to use."""
import random
from typing import Any, Dict, List

from .data import Customer, Transaction, get_customer_history, get_transaction_patterns


class PaymentTools:
    """Tools for payment risk assessment agents."""

    def __init__(self, customers: List[Customer], transactions: List[Transaction]):
        self.customers = customers
        self.transactions = transactions

    def get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer KYC and history."""
        return get_customer_history(customer_id, self.customers)

    def get_transaction_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's recent transaction patterns."""
        return get_transaction_patterns(customer_id, self.transactions)

    def calculate_fraud_score(self, customer_id: str, amount: float) -> Dict[str, Any]:
        """
        Calculate fraud probability (0-100).

        Uses a simple heuristic based on customer history and transaction
        amount deviation; a production system would use an ML model.
        """
        history = self.get_customer_profile(customer_id)
        transaction_patterns = self.get_transaction_history(customer_id)

        score = 10  # Baseline risk

        # Increase score if fraud history
        if history.get("fraud_history") == "yes":
            score += 30

        # Increase score for unusual amount relative to customer average
        avg_amount = transaction_patterns.get("average_amount", 0)
        if avg_amount > 0 and amount > avg_amount * 2.5:
            score += 20

        # Decrease score for VIP status (trusted customer)
        if history.get("vip_status") == "yes":
            score -= 15

        # Decrease score for long account tenure
        account_age = history.get("account_age_years", 0)
        if account_age > 5:
            score -= 10

        return {
            "fraud_score": max(0, min(100, score)),  # Clamp to [0, 100]
            "reasoning": (
                "Based on customer history, transaction patterns, and amount deviation"
            ),
        }

    def check_velocity(self, customer_id: str, amount: float) -> Dict[str, Any]:
        """Check for transaction velocity anomalies against account limit."""
        history = self.get_customer_profile(customer_id)

        account_limit = history.get("account_limit", 10000)
        velocity_ok = amount < account_limit * 0.5

        return {
            "velocity_ok": velocity_ok,
            "amount": amount,
            "account_limit": account_limit,
            "percentage_of_limit": round((amount / account_limit) * 100, 2),
            "risk": "low" if velocity_ok else "high",
        }

    def check_sanctions(self, customer_id: str) -> Dict[str, Any]:
        """
        Check if customer is on sanctions list (stub implementation).

        In production this would query OFAC / UN / EU sanctions databases.
        The random seed is fixed per customer_id to ensure determinism.
        """
        rng = random.Random(customer_id)
        is_sanctioned = rng.random() < 0.01  # ~1% flagged

        return {
            "is_sanctioned": is_sanctioned,
            "status": "flagged" if is_sanctioned else "clear",
        }

    def apply_business_rules(
        self, fraud_score: float, velocity_ok: bool
    ) -> Dict[str, Any]:
        """Apply hard business rules to produce an approval decision."""
        if fraud_score > 70 or not velocity_ok:
            return {
                "decision": "DECLINE",
                "reason": "High fraud score or velocity violation",
            }
        elif fraud_score > 40:
            return {
                "decision": "REVIEW",
                "reason": "Medium fraud score, requires human review",
            }
        else:
            return {
                "decision": "APPROVE",
                "reason": "Low risk, auto-approved",
            }


def create_tools(
    customers: List[Customer], transactions: List[Transaction]
) -> PaymentTools:
    """Factory function to create a configured PaymentTools instance."""
    return PaymentTools(customers, transactions)
