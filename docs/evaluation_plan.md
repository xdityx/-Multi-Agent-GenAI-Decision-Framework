# Evaluation Plan

## Evaluation Philosophy

This project evaluates decision orchestration quality, not real-world fraud, churn, or payment prediction accuracy.

Because the current data is synthetic/sample data, evaluation should focus on workflow behavior, traceability, consistency, fallback reliability, and coverage of known rule paths. Real accuracy evaluation would require labeled production-like datasets and separate domain validation.

## Decision Consistency

Goal: verify that identical inputs produce stable decisions in heuristic mode.

Checks:

- Run the same request multiple times and compare final decisions.
- Confirm deterministic scoring for fixed synthetic/sample data.
- Confirm each domain maps known input patterns to expected action labels.
- Track decision distribution across sample IDs to identify obvious rule gaps.

Useful metrics:

- same-input decision match rate
- unexpected decision label count
- invalid or missing score count

## Trace Completeness

Goal: ensure every workflow returns a complete auditable trace.

Checks:

- Confirm each response includes `agent_outputs`.
- Confirm each agent output includes agent name, analysis, tools used, and reasoning where available.
- Confirm the agent sequence is ordered correctly.
- Confirm the final result includes domain, decision, decision score, and final reasoning.

Useful metrics:

- trace completeness rate
- missing field count
- invalid agent sequence count

## Fallback Reliability

Goal: ensure the system remains runnable when LLM providers or API keys are unavailable.

Checks:

- Run LLM-mode workflows without provider keys.
- Simulate provider failures where practical.
- Confirm deterministic mock fallback returns structured outputs.
- Confirm tests do not require paid or live LLM access.

Useful metrics:

- fallback success rate
- fallback latency
- malformed fallback output count
- provider error handling pass rate

## RAG Retrieval Sanity

Goal: verify that the RAG layer returns relevant sample policy context.

Checks:

- Query domain-specific terms such as payment review, retention outreach, and fraud challenge.
- Confirm top-k retrieval returns documents from the correct domain.
- Confirm empty retrieval cases are handled gracefully.
- Confirm formatted context is readable and usable by LLM agents.

Useful metrics:

- top-k non-empty retrieval rate
- domain relevance spot-check rate
- empty-result handling pass rate
- formatted-context validity count

## Latency

Goal: measure whether the workflow is responsive enough for demos and identify future production bottlenecks.

Checks:

- Measure end-to-end latency for each domain in heuristic mode.
- Measure end-to-end latency for LLM + RAG mode with live providers when configured.
- Track latency contribution from RAG retrieval and LLM calls separately where possible.
- Compare Streamlit standalone mode against FastAPI mode.

Useful metrics:

- p50, p95, and max workflow latency
- RAG retrieval latency
- LLM call latency
- fallback latency

## Rule Coverage

Goal: ensure heuristic rules and action mappings are exercised by tests and sample requests.

Checks:

- Identify each possible action label per domain.
- Create sample requests or test fixtures that trigger each action.
- Confirm edge cases are handled, such as invalid IDs or unusual transaction amounts.
- Confirm decision scores remain within expected ranges.

Useful metrics:

- action-label coverage
- rule-branch coverage
- invalid-input handling pass rate
- score range validation pass rate

## Suggested Evaluation Artifacts

For a stronger future version, add:

- a small evaluation report generated from test runs
- a matrix of domain action labels and triggering fixtures
- latency benchmarks for heuristic and LLM + RAG modes
- trace completeness checks in CI
- prompt and RAG document version metadata

## Production Evaluation Requirements

Before any production use, the framework would need:

- real labeled data for each domain
- business-approved metrics and thresholds
- calibration analysis for scores
- drift and monitoring strategy
- fairness and bias checks where relevant
- human review and escalation workflows
- security, compliance, and audit review

