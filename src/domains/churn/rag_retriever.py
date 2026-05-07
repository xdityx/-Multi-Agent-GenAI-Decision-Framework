"""RAG retriever for the churn domain.

Uses keyword-scoring only (no ChromaDB) — the churn domain is intentionally
lightweight to contrast with the payments domain's vector-store approach.
This demonstrates that the framework is flexible: domains can choose the
retrieval strategy that fits their needs.
"""
from typing import Any, Dict, List

from .rag_documents import RETENTION_POLICIES


class ChurnRAGRetriever:
    """Retrieves relevant retention policies via keyword scoring."""

    def __init__(self) -> None:
        self.policies = RETENTION_POLICIES

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return the *top_k* most relevant policies for *query*."""
        query_lower = query.lower()
        scored: List[Dict[str, Any]] = []

        for policy in self.policies:
            score = 0
            if query_lower in policy["title"].lower():
                score += 10
            for word in query_lower.split():
                score += policy["content"].lower().count(word)

            if score > 0:
                scored.append(
                    {
                        "id": policy["id"],
                        "title": policy["title"],
                        "content": policy["content"],
                        "score": score,
                    }
                )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into an LLM-ready context block."""
        if not documents:
            return "No relevant retention policies found."

        lines = ["## Relevant Retention Policies:\n"]
        for doc in documents:
            lines.append(f"### {doc['title']}")
            lines.append(doc["content"])
            lines.append("")
        return "\n".join(lines)
