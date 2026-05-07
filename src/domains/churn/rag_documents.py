"""RAG documents for churn domain — customer retention policies and strategies."""
from typing import Any, Dict, List


RETENTION_POLICIES: List[Dict[str, str]] = [
    {
        "id": "policy_churn_001",
        "title": "Churn Risk Thresholds",
        "content": (
            "Customer churn risk levels:\n"
            "- Low risk: churn probability < 20%\n"
            "- Medium risk: churn probability 20-50%\n"
            "- High risk: churn probability > 50%\n\n"
            "For high-risk customers, initiate immediate retention action.\n"
            "For medium-risk, monitor and reach out proactively.\n"
            "For low-risk, continue standard engagement."
        ),
    },
    {
        "id": "policy_engagement_001",
        "title": "Engagement Metrics and Signals",
        "content": (
            "Key engagement signals for churn prediction:\n"
            "- Login frequency: Daily active > 5x/week = healthy\n"
            "- Feature adoption: Using >70% of features = healthy\n"
            "- Support interactions: >1 ticket/month = engagement\n"
            "- NPS score: >50 = positive, <30 = at-risk\n"
            "- Usage trends: Increasing usage = healthy, declining = at-risk\n\n"
            "Declining trends on any metric indicate churn risk."
        ),
    },
    {
        "id": "policy_retention_001",
        "title": "Retention Strategies by Segment",
        "content": (
            "Targeted retention actions by customer segment:\n\n"
            "VIP Customers (High LTV):\n"
            "- Dedicated account manager\n"
            "- Priority support\n"
            "- Custom feature requests\n"
            "- Executive check-ins quarterly\n\n"
            "Regular Customers:\n"
            "- Personalized email campaigns\n"
            "- Feature tips and tutorials\n"
            "- Community engagement\n"
            "- Discount/renewal incentives\n\n"
            "At-Risk Customers:\n"
            "- Immediate outreach call\n"
            "- Custom discount (up to 30%)\n"
            "- Root cause analysis\n"
            "- Executive engagement if C-level"
        ),
    },
    {
        "id": "policy_ltv_001",
        "title": "Customer Lifetime Value and Retention ROI",
        "content": (
            "Retention ROI guidelines:\n"
            "- VIP (LTV > $50k): Spend up to 20% of LTV on retention\n"
            "- Standard (LTV $5k-50k): Spend up to 10% of LTV on retention\n"
            "- Basic (LTV < $5k): Spend up to 5% of LTV on retention\n\n"
            "Cost of retention is always less than cost of acquisition.\n"
            "Acquisition cost is typically 5-25x retention cost.\n\n"
            "Prioritize retention for high-LTV customers."
        ),
    },
    {
        "id": "pattern_churn_001",
        "title": "Common Churn Patterns",
        "content": (
            "Early warning signs of churn:\n"
            "1. Support ticket spike: Sudden increase in complaints\n"
            "2. Feature abandonment: Stopped using core features\n"
            "3. Login decline: Decreasing login frequency\n"
            "4. Interaction drop: Reduced support/sales interactions\n"
            "5. Competitive mention: Mentions of competitors in support\n"
            "6. Contract renewal: No renewal within 60 days of expiry\n"
            "7. Budget concerns: Price objections or budget cuts mentioned\n\n"
            "Multiple concurrent signals = high churn probability.\n"
            "Act within 7 days of first signal for best retention rates."
        ),
    },
]


def get_rag_documents() -> List[Dict[str, Any]]:
    """Return all retention policy documents."""
    return RETENTION_POLICIES


def get_policy_content(policy_id: str) -> str:
    """Fetch a specific policy's content by ID."""
    for policy in RETENTION_POLICIES:
        if policy["id"] == policy_id:
            return policy["content"]
    return "Policy not found"


def search_relevant_policies(query: str) -> List[Dict[str, Any]]:
    """Keyword search over retention policy titles and content."""
    query_lower = query.lower()
    results = []

    for policy in RETENTION_POLICIES:
        title_match = query_lower in policy["title"].lower()
        content_match = query_lower in policy["content"].lower()

        if title_match or content_match:
            results.append(
                {
                    "id": policy["id"],
                    "title": policy["title"],
                    "excerpt": policy["content"][:200] + "...",
                }
            )

    return results
