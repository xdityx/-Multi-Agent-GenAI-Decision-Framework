"""Tests for the churn domain — heuristic agents, LLM agents, and workflows."""
import pytest

from src.core.schemas import DecisionRequest
from src.core.workflow import DecisionWorkflow
from src.domains.churn.agents import (
    ChurnDataAgent,
    ChurnDecisionAgent,
    ChurnExplanationAgent,
    ChurnRiskAgent,
)
from src.domains.churn.agents_llm import (
    LLMChurnAnalysisAgent,
    LLMRetentionDecisionAgent,
    LLMRetentionExplainerAgent,
)
from src.domains.churn.data import ChurnDataGenerator
from src.domains.churn.rag_documents import (
    RETENTION_POLICIES,
    get_policy_content,
    search_relevant_policies,
)
from src.domains.churn.rag_retriever import ChurnRAGRetriever
from src.domains.churn.tools import create_tools

VALID_ACTIONS = {
    "EXECUTIVE_OUTREACH",
    "URGENT_RETENTION",
    "PROACTIVE_OUTREACH",
    "STANDARD_ENGAGEMENT",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def churn_customers():
    """Generate 50 deterministic customers (seed=42)."""
    return ChurnDataGenerator(seed=42).generate_customers(count=50)


@pytest.fixture(scope="module")
def churn_tools(churn_customers):
    return create_tools(churn_customers)


@pytest.fixture(scope="module")
def rag_retriever():
    return ChurnRAGRetriever()


# ---------------------------------------------------------------------------
# RAG document tests
# ---------------------------------------------------------------------------


def test_retention_policies_count():
    """Policy corpus contains exactly 5 documents."""
    assert len(RETENTION_POLICIES) == 5


def test_policy_ids_unique():
    """Every policy has a unique ID."""
    ids = [p["id"] for p in RETENTION_POLICIES]
    assert len(ids) == len(set(ids))


def test_get_policy_content_found():
    """Known policy ID returns its content."""
    content = get_policy_content("policy_churn_001")
    assert "churn" in content.lower()


def test_get_policy_content_missing():
    """Unknown policy ID returns sentinel string."""
    assert get_policy_content("nonexistent") == "Policy not found"


def test_search_policies_hit():
    """Keyword search finds at least one match for 'churn'."""
    results = search_relevant_policies("churn")
    assert len(results) >= 1
    assert all("id" in r and "title" in r and "excerpt" in r for r in results)


def test_search_policies_no_hit():
    """Irrelevant query returns empty list."""
    assert search_relevant_policies("xyzzy_no_match") == []


# ---------------------------------------------------------------------------
# RAG retriever tests
# ---------------------------------------------------------------------------


def test_rag_retriever_init(rag_retriever):
    """Retriever has all five policies loaded."""
    assert len(rag_retriever.policies) == 5


def test_rag_retriever_returns_docs(rag_retriever):
    """retrieve() returns documents for a relevant query."""
    docs = rag_retriever.retrieve("churn retention", top_k=3)
    assert len(docs) >= 1
    assert "title" in docs[0]
    assert "content" in docs[0]


def test_rag_retriever_top_k(rag_retriever):
    """retrieve() never exceeds top_k."""
    docs = rag_retriever.retrieve("customer", top_k=2)
    assert len(docs) <= 2


def test_rag_format_context(rag_retriever):
    """format_context() produces a labelled context block."""
    docs = rag_retriever.retrieve("churn", top_k=2)
    ctx = rag_retriever.format_context(docs)
    assert "Relevant Retention Policies" in ctx


def test_rag_format_context_empty(rag_retriever):
    """format_context([]) returns the 'no policies' sentinel."""
    assert "No relevant retention policies found" in rag_retriever.format_context([])


# ---------------------------------------------------------------------------
# Data + tool tests
# ---------------------------------------------------------------------------


def test_churn_data_generation(churn_customers):
    """Generator produces the right count with correct first ID."""
    assert len(churn_customers) == 50
    assert churn_customers[0].customer_id == "CUST_00000"


def test_customer_ids_unique(churn_customers):
    """All generated customer IDs are unique."""
    ids = [c.customer_id for c in churn_customers]
    assert len(ids) == len(set(ids))


def test_churn_tools_profile(churn_tools):
    """get_customer_data returns expected fields."""
    profile = churn_tools.get_customer_data("CUST_00000")
    assert profile["customer_id"] == "CUST_00000"
    assert "nps_score" in profile
    assert "login_frequency" in profile


def test_churn_tools_unknown_customer(churn_tools):
    """Unknown customer ID returns an error dict."""
    result = churn_tools.get_customer_data("CUST_XXXXX")
    assert "error" in result


def test_churn_tools_churn_score(churn_tools):
    """calculate_churn_score returns a score in [0, 100]."""
    result = churn_tools.calculate_churn_score("CUST_00000")
    assert 0 <= result["churn_score"] <= 100
    assert "reasoning" in result


def test_churn_tools_customer_value(churn_tools):
    """calculate_customer_value returns ltv, tier, and retention_budget."""
    result = churn_tools.calculate_customer_value("CUST_00000")
    assert "ltv" in result
    assert "tier" in result
    assert result["tier"] in {"VIP", "Standard", "Basic"}
    assert result["retention_budget"] >= 0


def test_retention_action_high_risk_vip(churn_tools):
    """High churn + VIP tier → EXECUTIVE_OUTREACH."""
    result = churn_tools.determine_retention_action(
        80, {"tier": "VIP", "ltv": 100_000, "retention_budget": 20_000}
    )
    assert result["recommended_action"] == "EXECUTIVE_OUTREACH"
    assert result["urgency"] == "HIGH"


def test_retention_action_high_risk_standard(churn_tools):
    """High churn + Standard tier → URGENT_RETENTION."""
    result = churn_tools.determine_retention_action(
        80, {"tier": "Standard", "ltv": 10_000, "retention_budget": 1_000}
    )
    assert result["recommended_action"] == "URGENT_RETENTION"


def test_retention_action_medium_risk(churn_tools):
    """Medium churn → PROACTIVE_OUTREACH."""
    result = churn_tools.determine_retention_action(
        50, {"tier": "Standard", "ltv": 10_000, "retention_budget": 1_000}
    )
    assert result["recommended_action"] == "PROACTIVE_OUTREACH"
    assert result["urgency"] == "MEDIUM"


def test_retention_action_low_risk(churn_tools):
    """Low churn → STANDARD_ENGAGEMENT."""
    result = churn_tools.determine_retention_action(
        20, {"tier": "Basic", "ltv": 3_000, "retention_budget": 150}
    )
    assert result["recommended_action"] == "STANDARD_ENGAGEMENT"
    assert result["urgency"] == "LOW"


# ---------------------------------------------------------------------------
# Heuristic agent tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_churn_data_agent(churn_tools):
    """ChurnDataAgent populates customer_profile and engagement_trends."""
    agent = ChurnDataAgent(churn_tools)
    output = await agent.run({"customer_id": "CUST_00000"})

    assert output.agent_name == "churn_data_agent"
    assert "customer_profile" in output.analysis
    assert "engagement_trends" in output.analysis


@pytest.mark.asyncio
async def test_churn_risk_agent(churn_tools):
    """ChurnRiskAgent produces churn_score and customer_tier."""
    agent = ChurnRiskAgent(churn_tools)
    output = await agent.run({"customer_id": "CUST_00000"})

    assert output.agent_name == "churn_risk_agent"
    assert "churn_score" in output.analysis
    assert output.analysis["churn_category"] in {"HIGH", "MEDIUM", "LOW"}


@pytest.mark.asyncio
async def test_churn_decision_agent(churn_tools):
    """ChurnDecisionAgent maps risk analysis to a valid action."""
    agent = ChurnDecisionAgent(churn_tools)
    context = {
        "previous_agent_output": {
            "churn_score": 65,
            "ltv": 10_000,
            "customer_tier": "Standard",
            "retention_budget": 1_000,
        }
    }
    output = await agent.run(context)

    assert output.agent_name == "churn_decision_agent"
    assert output.analysis["decision"] in VALID_ACTIONS
    assert 0.0 <= output.analysis["score"] <= 1.0


@pytest.mark.asyncio
async def test_churn_explanation_agent(churn_tools):
    """ChurnExplanationAgent produces a non-empty explanation."""
    agent = ChurnExplanationAgent(churn_tools)
    context = {
        "previous_agent_output": {
            "decision": "URGENT_RETENTION",
            "urgency": "HIGH",
            "score": 0.3,
        }
    }
    output = await agent.run(context)

    assert output.agent_name == "churn_explanation_agent"
    assert "URGENT_RETENTION" in output.analysis["explanation"]


# ---------------------------------------------------------------------------
# LLM agent tests (mock mode — no API key required)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_llm_churn_analysis_agent(rag_retriever):
    """LLMChurnAnalysisAgent produces expected output keys in mock mode."""
    agent = LLMChurnAnalysisAgent(rag_retriever)
    context = {
        "customer_id": "CUST_00000",
        "previous_agent_output": {
            "customer_profile": {"customer_id": "CUST_00000", "nps_score": 45},
            "engagement_trends": {"login_trend": "declining"},
        },
    }
    output = await agent.run(context)

    assert output.agent_name == "llm_churn_analysis_agent"
    assert "churn_analysis" in output.analysis
    assert output.analysis["rag_enabled"] is True
    assert isinstance(output.analysis["retrieved_policies"], list)


@pytest.mark.asyncio
async def test_llm_retention_decision_agent(rag_retriever):
    """LLMRetentionDecisionAgent maps to a valid action in mock mode."""
    agent = LLMRetentionDecisionAgent(rag_retriever)
    context = {
        "previous_agent_output": {
            "churn_analysis": "High churn risk — login frequency dropped to 1/week.",
        }
    }
    output = await agent.run(context)

    assert output.agent_name == "llm_retention_decision_agent"
    assert output.analysis["decision"] in VALID_ACTIONS
    assert 0.0 <= output.analysis["score"] <= 1.0


@pytest.mark.asyncio
async def test_llm_retention_explainer_agent():
    """LLMRetentionExplainerAgent produces a non-empty explanation in mock mode."""
    agent = LLMRetentionExplainerAgent()
    context = {
        "previous_agent_output": {
            "decision": "PROACTIVE_OUTREACH",
            "llm_reasoning": "Medium risk; personalised outreach recommended.",
        }
    }
    output = await agent.run(context)

    assert output.agent_name == "llm_retention_explainer_agent"
    assert len(output.analysis["explanation"]) > 10
    assert output.analysis["llm_generated"] is True


# ---------------------------------------------------------------------------
# Workflow tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_heuristic_workflow_end_to_end(churn_tools):
    """Full 4-agent heuristic churn workflow produces a valid DecisionResult."""
    agents = [
        ChurnDataAgent(churn_tools),
        ChurnRiskAgent(churn_tools),
        ChurnDecisionAgent(churn_tools),
        ChurnExplanationAgent(churn_tools),
    ]
    workflow = DecisionWorkflow(agents, "churn_heuristic_workflow")

    request = DecisionRequest(
        domain="churn",
        entity_id="CUST_00000",
        context={"customer_id": "CUST_00000"},
    )
    result = await workflow.execute(request)

    assert result.domain == "churn"
    assert len(result.agent_outputs) == 4
    assert result.decision in VALID_ACTIONS


@pytest.mark.asyncio
async def test_llm_workflow_end_to_end(rag_retriever):
    """Full 3-agent LLM churn workflow produces a valid DecisionResult."""
    agents = [
        LLMChurnAnalysisAgent(rag_retriever),
        LLMRetentionDecisionAgent(rag_retriever),
        LLMRetentionExplainerAgent(),
    ]
    workflow = DecisionWorkflow(agents, "churn_llm_workflow")

    request = DecisionRequest(
        domain="churn",
        entity_id="CUST_00000",
        context={"customer_id": "CUST_00000"},
    )
    result = await workflow.execute(request)

    assert result.domain == "churn"
    assert len(result.agent_outputs) == 3
    assert result.decision in VALID_ACTIONS
