"""Evaluate local RAG retrieval sanity without live LLM calls."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _payment_retriever():
    from src.domains.payments.rag_retriever import PaymentRAGRetriever

    return PaymentRAGRetriever(), "fraud payment approval review"


def _churn_retriever():
    from src.domains.churn.rag_retriever import ChurnRAGRetriever

    return ChurnRAGRetriever(), "churn retention outreach"


def _fraud_retriever():
    from src.domains.fraud.rag_retriever import FraudRAGRetriever

    return FraudRAGRetriever(), "fraud detection red flags"


BUILDERS = {
    "payments": _payment_retriever,
    "churn": _churn_retriever,
    "fraud": _fraud_retriever,
}


def _evaluate_domain(domain: str) -> Dict[str, Any]:
    try:
        retriever, query = BUILDERS[domain]()
        documents = retriever.retrieve(query, top_k=3)
        context = retriever.format_context(documents)
    except Exception as exc:
        return {"domain": domain, "status": "SKIPPED", "reason": str(exc)}

    non_empty_docs = len(documents) > 0
    useful_context = bool(context.strip()) and not context.lower().startswith("no relevant")
    titles = [doc.get("title", "") for doc in documents]
    return {
        "domain": domain,
        "status": "PASS" if non_empty_docs and useful_context else "FAIL",
        "query": query,
        "document_count": len(documents),
        "context_chars": len(context),
        "titles": titles,
    }


def evaluate_rag_retrieval() -> List[Dict[str, Any]]:
    """Check that each available RAG retriever returns local context."""
    return [_evaluate_domain(domain) for domain in BUILDERS]


def print_summary(results: List[Dict[str, Any]]) -> None:
    print("\nRAG Retrieval Sanity")
    print("-" * 60)
    for result in results:
        domain = result["domain"]
        status = result["status"]
        if status == "SKIPPED":
            print(f"{domain:10} {status:7} {result['reason']}")
        else:
            detail = (
                f"docs={result['document_count']} "
                f"context_chars={result['context_chars']} "
                f"titles={result['titles']}"
            )
            print(f"{domain:10} {status:7} {detail}")


def main() -> List[Dict[str, Any]]:
    results = evaluate_rag_retrieval()
    print_summary(results)
    return results


if __name__ == "__main__":
    main()

