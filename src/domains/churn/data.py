"""Synthetic churn data for testing and demo."""
import random
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Customer:
    customer_id: str
    account_age_days: int
    ltv_amount: float
    nps_score: int          # 0-100
    login_frequency: int    # logins per week
    feature_adoption: float # 0.0-1.0
    support_tickets_count: int
    last_login_days_ago: int
    is_vip: bool


class ChurnDataGenerator:
    """Generate synthetic churn customer data."""

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_customers(self, count: int = 100) -> List[Customer]:
        """Generate *count* synthetic customers (deterministic with seed)."""
        customers = []
        for i in range(count):
            is_vip = random.random() < 0.1  # 10% VIP

            ltv = (
                random.choice([5000, 15000, 50000, 100000])
                if is_vip
                else random.uniform(2000, 20000)
            )

            customers.append(
                Customer(
                    customer_id=f"CUST_{i:05d}",
                    account_age_days=random.randint(30, 1825),
                    ltv_amount=ltv,
                    nps_score=random.randint(0, 100),
                    login_frequency=random.randint(0, 7),
                    feature_adoption=random.uniform(0.3, 1.0),
                    support_tickets_count=random.randint(0, 20),
                    last_login_days_ago=random.randint(0, 60),
                    is_vip=is_vip,
                )
            )
        return customers


def get_customer_profile(
    customer_id: str, customers: List[Customer]
) -> Dict[str, Any]:
    """Retrieve a customer profile dict by ID."""
    for customer in customers:
        if customer.customer_id == customer_id:
            return {
                "customer_id": customer_id,
                "account_age_days": customer.account_age_days,
                "ltv_amount": round(customer.ltv_amount, 2),
                "nps_score": customer.nps_score,
                "login_frequency": customer.login_frequency,
                "feature_adoption": round(customer.feature_adoption, 2),
                "support_tickets": customer.support_tickets_count,
                "last_login_days_ago": customer.last_login_days_ago,
                "is_vip": customer.is_vip,
            }
    return {"error": f"Customer {customer_id} not found"}


def get_engagement_trends(
    customer_id: str, customers: List[Customer]
) -> Dict[str, Any]:
    """Derive simple engagement trend labels from raw customer attributes."""
    for customer in customers:
        if customer.customer_id == customer_id:
            if customer.login_frequency < 2:
                login_trend = "declining"
            elif customer.login_frequency > 5:
                login_trend = "growing"
            else:
                login_trend = "stable"

            return {
                "login_trend": login_trend,
                "feature_adoption_trend": (
                    "stable" if customer.feature_adoption > 0.6 else "declining"
                ),
                "support_trend": (
                    "increasing" if customer.support_tickets_count > 5 else "stable"
                ),
                "nps_trend": (
                    "positive" if customer.nps_score > 50 else "negative"
                ),
            }
    return {"error": f"Customer {customer_id} not found"}
