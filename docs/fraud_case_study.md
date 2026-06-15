# Fraud Case Study

## Business Problem

Fraud operations teams need to decide whether a transaction should be approved, monitored, challenged, or blocked. A useful system should provide not only an action, but also a traceable explanation that supports review.

This project demonstrates fraud decision orchestration using synthetic/sample transaction data. It does not claim real fraud detection accuracy and is not a trained fraud model.

## Input Data

The fraud workflow uses sample inputs such as:

- transaction ID, such as `TXN_00000005`
- synthetic transaction attributes
- synthetic risk indicators
- optional sample fraud policy documents for LLM + RAG mode

The data is generated for demos and tests. It is not a real transaction dataset.

## Agent Flow

1. Fraud Data Agent loads synthetic transaction context.
2. Fraud Risk Agent or LLM Fraud Analysis Agent evaluates the transaction.
3. Fraud Decision Agent or LLM Fraud Decision Agent selects an action.
4. Fraud Explanation Agent or LLM Fraud Explainer Agent explains the action.
5. The workflow returns the decision and complete agent trace.

## Decision Logic

The heuristic path uses deterministic fraud-related rules over synthetic transaction features. The LLM + RAG path retrieves sample fraud policy context and uses LLM-backed reasoning when available.

Possible decisions:

- `BLOCK`
- `CHALLENGE`
- `MONITOR`
- `APPROVE`

These are demonstration actions and should not be treated as operational fraud recommendations.

## Example Request

```json
{
  "transaction_id": "TXN_00000005",
  "agent_type": "llm"
}
```

API endpoint:

```text
POST /analyze/fraud
```

## Example Response Shape

```json
{
  "domain": "fraud",
  "decision": "MONITOR",
  "decision_score": 0.58,
  "reasoning": "Human-readable fraud action rationale.",
  "agent_outputs": [
    {
      "agent": "fraud_data_agent",
      "analysis": {}
    },
    {
      "agent": "llm_fraud_analysis_agent",
      "analysis": {}
    },
    {
      "agent": "llm_fraud_decision_agent",
      "analysis": {}
    },
    {
      "agent": "llm_fraud_explainer_agent",
      "analysis": {}
    }
  ],
  "agent_type": "llm"
}
```

## Business Impact

This case study demonstrates how fraud workflows can be structured around explainable steps:

- collect transaction context
- evaluate risk indicators
- select an action
- explain the action
- preserve the trace for review

The interview value is the architecture: a reusable workflow can support multiple domains while keeping each domain's rules, documents, and action labels separate.

## Limitations

- Uses synthetic/sample transaction data only.
- Does not claim real fraud detection accuracy.
- Does not include labeled fraud outcomes, chargeback data, or investigator feedback.
- Does not include production-grade case management or real-time enforcement.
- LLM mode can fall back to deterministic mock output if providers are unavailable.

## Future Improvements

- Evaluate with labeled fraud outcomes.
- Add human investigator review queues.
- Add feedback loops from fraud outcomes and disputes.
- Add model/rule/prompt versioning.
- Add real-time latency and fallback monitoring.
- Integrate audit storage and compliance reporting.

