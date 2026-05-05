"""Synthetic payment data for testing and demo."""
import random
from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class Customer:
    customer_id: str
    account_age_years: int
    total_transactions: int
    fraud_history: bool
    average_transaction_amount: float
    account_limit: float
    vip_status: bool


@dataclass
class Transaction:
    transaction_id: str
    customer_id: str
    amount: float
    merchant: str
    mcc_code: str  # Merchant Category Code
    location: str
    timestamp: str
    is_fraudulent: bool


class PaymentDataGenerator:
    """Generate synthetic payment data."""

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_customers(self, count: int = 100) -> List[Customer]:
        """Generate synthetic customers."""
        customers = []
        for i in range(count):
            customers.append(
                Customer(
                    customer_id=f"CUST_{i:05d}",
                    account_age_years=random.randint(1, 10),
                    total_transactions=random.randint(10, 500),
                    fraud_history=random.random() < 0.05,  # 5% have fraud history
                    average_transaction_amount=random.uniform(100, 5000),
                    account_limit=random.choice([5000, 10000, 25000, 50000]),
                    vip_status=random.random() < 0.1,  # 10% VIP
                )
            )
        return customers

    def generate_transactions(
        self, customers: List[Customer], count: int = 50
    ) -> List[Transaction]:
        """Generate synthetic transactions."""
        transactions = []
        merchants = [
            "Amazon", "Flipkart", "Swiggy", "Uber",
            "Netflix", "Spotify", "Apple", "Google",
        ]
        mccs = ["5411", "5412", "4121", "7393", "5732", "4814", "5999"]
        locations = ["Mumbai", "Bangalore", "Delhi", "Pune", "Hyderabad", "Chennai"]

        for i in range(count):
            customer = random.choice(customers)
            amount = random.uniform(50, 10000)

            # 10% are actually fraudulent
            is_fraud = random.random() < 0.10

            transactions.append(
                Transaction(
                    transaction_id=f"TXN_{i:08d}",
                    customer_id=customer.customer_id,
                    amount=amount,
                    merchant=random.choice(merchants),
                    mcc_code=random.choice(mccs),
                    location=random.choice(locations),
                    timestamp=(
                        f"2026-05-04T"
                        f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
                    ),
                    is_fraudulent=is_fraud or customer.fraud_history,
                )
            )
        return transactions


def get_customer_history(
    customer_id: str, customers: List[Customer]
) -> Dict[str, Any]:
    """Get customer profile from data."""
    for customer in customers:
        if customer.customer_id == customer_id:
            return {
                "customer_id": customer_id,
                "account_age_years": customer.account_age_years,
                "total_transactions": customer.total_transactions,
                "fraud_history": "yes" if customer.fraud_history else "no",
                "average_transaction_amount": round(
                    customer.average_transaction_amount, 2
                ),
                "account_limit": customer.account_limit,
                "vip_status": "yes" if customer.vip_status else "no",
            }
    return {"error": f"Customer {customer_id} not found"}


def get_transaction_patterns(
    customer_id: str, transactions: List[Transaction]
) -> Dict[str, Any]:
    """Get transaction patterns for customer."""
    customer_txns = [t for t in transactions if t.customer_id == customer_id]
    if not customer_txns:
        return {"error": f"No transactions found for {customer_id}"}

    amounts = [t.amount for t in customer_txns]
    return {
        "transaction_count": len(customer_txns),
        "average_amount": round(sum(amounts) / len(amounts), 2),
        "min_amount": min(amounts),
        "max_amount": max(amounts),
        "merchants_used": list(set(t.merchant for t in customer_txns)),
        "locations_used": list(set(t.location for t in customer_txns)),
    }
