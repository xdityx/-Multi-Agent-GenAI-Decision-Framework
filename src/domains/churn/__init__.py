"""Churn domain — heuristic and LLM agents for customer retention."""

# Heuristic agents
from .agents import (
    ChurnDataAgent,
    ChurnDecisionAgent,
    ChurnExplanationAgent,
    ChurnRiskAgent,
)

# LLM agents
from .agents_llm import (
    LLMChurnAnalysisAgent,
    LLMRetentionDecisionAgent,
    LLMRetentionExplainerAgent,
)

# Data, tools, RAG
from .data import ChurnDataGenerator
from .rag_documents import RETENTION_POLICIES
from .rag_retriever import ChurnRAGRetriever
from .tools import ChurnTools, create_tools

__all__ = [
    # Heuristic
    "ChurnDataAgent",
    "ChurnRiskAgent",
    "ChurnDecisionAgent",
    "ChurnExplanationAgent",
    # LLM
    "LLMChurnAnalysisAgent",
    "LLMRetentionDecisionAgent",
    "LLMRetentionExplainerAgent",
    # Tools & data
    "ChurnTools",
    "create_tools",
    "ChurnDataGenerator",
    # RAG
    "ChurnRAGRetriever",
    "RETENTION_POLICIES",
]
