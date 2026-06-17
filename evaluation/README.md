# Evaluation Scripts

These scripts evaluate the Multi-Agent GenAI Decision Framework as an explainable decision orchestration system.

They do not evaluate this project as a predictive ML model. The repository uses synthetic/sample data, so traditional ML metrics such as accuracy, precision, recall, F1, ROC AUC, and confusion matrices would be misleading. Those metrics would require labeled real-world or production-like datasets and a separate validation plan.

## What Is Evaluated

### Decision Consistency

Runs the same heuristic request multiple times for Payments, Churn, and Fraud. The check passes when the final decision and score remain stable for the same input.

Script:

```bash
python evaluation/evaluate_decision_consistency.py
```

### Trace Completeness

Verifies that each heuristic workflow returns the expected minimum agent sequence:

- data agent
- risk or analysis agent
- decision agent
- explanation agent

The check reports missing or out-of-order steps.

Script:

```bash
python evaluation/evaluate_trace_completeness.py
```

### Latency

Runs a small number of sample heuristic requests and reports average, minimum, and maximum latency per domain.

This is a lightweight local timing check for demos and development. It is not a production service-level benchmark.

Script:

```bash
python evaluation/evaluate_latency.py
```

### RAG Retrieval Sanity

Queries the local sample policy retrievers for Payments, Churn, and Fraud. The check passes when retrieval returns non-empty documents and usable formatted context.

This script does not make live LLM calls and should work without API keys. If an optional dependency or domain import is unavailable, the domain is reported as skipped rather than crashing the full run.

Script:

```bash
python evaluation/evaluate_rag_retrieval.py
```

## Run All Evaluations

From the project root:

```bash
python evaluation/run_all_evaluations.py
```

The runner prints a clean console summary with `PASS`, `FAIL`, and `SKIPPED` counts.

## Interpretation

These evaluations answer questions such as:

- Does the same request produce the same heuristic decision?
- Does every workflow return an auditable agent trace?
- Are local workflow latencies reasonable for a demo?
- Do the local RAG retrievers return policy context?
- Does the project remain runnable without live LLM API keys?

They do not answer:

- Is this a validated fraud model?
- Is this a validated churn model?
- Is this a production payment risk engine?
- What is the real-world predictive accuracy?

Those questions require labeled data, production controls, domain-specific validation, and human review workflows.

