"""LLM prompt templates for churn domain agents."""


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_CHURN_ANALYSIS = """You are a customer retention expert. \
Analyze the provided customer data and retention policies to determine churn risk.

Use chain-of-thought reasoning:
1. Identify customer engagement signals (login frequency, NPS, feature usage).
2. Check for early-warning patterns against the retrieved retention policies.
3. Synthesize a churn risk score (0-100) and a concrete retention recommendation.

Be specific about which factors are driving churn risk."""

SYSTEM_PROMPT_RETENTION_DECISION = """You are a retention strategy advisor. \
Given a churn analysis and retention policies, decide the best action:
- EXECUTIVE_OUTREACH  — for VIP customers at high risk
- URGENT_RETENTION    — for high-risk customers (discount + immediate call)
- PROACTIVE_OUTREACH  — for medium-risk customers (email + feature tips)
- STANDARD_ENGAGEMENT — for low-risk customers (normal cadence)

Respond with exactly one action label on the first line, \
followed by a 2-3 sentence justification based on LTV and risk level."""

SYSTEM_PROMPT_RETENTION_EXPLAINER = """You are a customer success communicator. \
Explain retention decisions clearly to a non-technical audience.

Format:
1. **Churn Risk**: Why the customer is at risk
2. **Retention Value**: Why we want to keep them (LTV, strategic importance)
3. **Recommended Action**: What we will do to retain them
4. **Next Steps**: Timeline and contact method

Be empathetic and action-oriented."""


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------


def get_churn_analysis_prompt(
    customer_profile: dict, engagement: dict, policies: str
) -> str:
    """Compose the churn-analysis user message."""
    return (
        "Analyze this customer for churn risk:\n\n"
        "**Customer Profile:**\n"
        f"- ID: {customer_profile.get('customer_id', 'N/A')}\n"
        f"- Account Age: {customer_profile.get('account_age_days', 'N/A')} days\n"
        f"- LTV: ${customer_profile.get('ltv_amount', 'N/A')}\n"
        f"- NPS Score: {customer_profile.get('nps_score', 'N/A')}/100\n"
        f"- VIP Status: {customer_profile.get('is_vip', False)}\n\n"
        "**Engagement Metrics:**\n"
        f"- Login Frequency: {customer_profile.get('login_frequency', 'N/A')} times/week\n"
        f"- Feature Adoption: {customer_profile.get('feature_adoption', 'N/A')}\n"
        f"- Support Tickets: {customer_profile.get('support_tickets', 'N/A')}\n"
        f"- Last Login: {customer_profile.get('last_login_days_ago', 'N/A')} days ago\n\n"
        f"**Engagement Trends:**\n{engagement}\n\n"
        f"**Retention Policies:**\n{policies}\n\n"
        "Analyze churn risk using chain-of-thought reasoning. "
        "Provide a churn score (0-100) and a detailed retention recommendation."
    )


def get_retention_decision_prompt(
    churn_analysis: str, ltv_data: dict, policies: str
) -> str:
    """Compose the retention-decision user message."""
    return (
        "Make a retention strategy decision for this customer.\n\n"
        f"**Churn Analysis:**\n{churn_analysis}\n\n"
        "**Customer Value:**\n"
        f"- LTV: ${ltv_data.get('ltv', 'N/A')}\n"
        f"- Tier: {ltv_data.get('tier', 'Unknown')}\n"
        f"- Retention Budget: ${ltv_data.get('retention_budget', 'N/A')}\n\n"
        f"**Retention Policies:**\n{policies}\n\n"
        "Decide: EXECUTIVE_OUTREACH, URGENT_RETENTION, PROACTIVE_OUTREACH, "
        "or STANDARD_ENGAGEMENT\n"
        "Explain your reasoning in 2-3 sentences."
    )


def get_retention_explanation_prompt(churn_risk: str, retention_action: str) -> str:
    """Compose the explanation user message."""
    return (
        "Explain this retention strategy to a non-technical audience:\n\n"
        f"**Churn Risk**: {churn_risk}\n"
        f"**Recommended Action**: {retention_action}\n\n"
        "Write a clear, empathetic explanation (2-3 sentences) covering:\n"
        "1. Why the customer is at risk\n"
        "2. Why we want to keep them\n"
        "3. What we will do to retain them\n\n"
        "Be positive but honest about the risk."
    )
