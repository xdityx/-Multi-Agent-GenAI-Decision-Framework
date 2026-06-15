# Churn Case Study

## Business Problem

Customer success and retention teams need to decide which customers should receive outreach and what level of intervention is appropriate. The challenge is to make the decision explainable, not just to produce a churn label.

This project demonstrates churn-related decision orchestration using synthetic/sample customer data. It does not claim real churn prediction accuracy and is not a trained churn model.

## Input Data

The churn workflow uses sample inputs such as:

- customer ID, such as `CUST_00012`
- synthetic engagement profile
- synthetic account or usage signals
- optional sample retention policy documents for LLM + RAG mode

The data is generated for local demos and tests. It is not real customer history.

## Agent Flow

1. Churn Data Agent loads synthetic customer context.
2. Churn Risk Agent or LLM Churn Analysis Agent evaluates retention risk.
3. Churn Decision Agent or LLM Retention Decision Agent selects an outreach action.
4. Churn Explanation Agent or LLM Retention Explainer Agent explains the decision.
5. The workflow returns the selected action and full agent trace.

## Decision Logic

The heuristic path uses local rules and synthetic engagement signals. The LLM + RAG path retrieves sample retention guidance and uses that context to support reasoning.

Possible decisions:

- `EXECUTIVE_OUTREACH`
- `URGENT_RETENTION`
- `PROACTIVE_OUTREACH`
- `STANDARD_ENGAGEMENT`

These are demonstration actions. They should not be interpreted as validated churn predictions.

## Example Request

```json
{
  "customer_id": "CUST_00012",
  "agent_type": "heuristic"
}
```

API endpoint:

```text
POST /analyze/churn
```

## Example Response Shape

```json
{
  "domain": "churn",
  "decision": "PROACTIVE_OUTREACH",
  "decision_score": 0.64,
  "reasoning": "Human-readable retention action rationale.",
  "agent_outputs": [
    {
      "agent": "churn_data_agent",
      "analysis": {}
    },
    {
      "agent": "churn_risk_agent",
      "analysis": {}
    },
    {
      "agent": "churn_decision_agent",
      "analysis": {}
    },
    {
      "agent": "churn_explanation_agent",
      "analysis": {}
    }
  ],
  "agent_type": "heuristic"
}
```

## Business Impact

This case study shows how retention decisions can be made more transparent by separating context gathering, risk analysis, action selection, and explanation.

For recruiters and interviewers, the value is the system design pattern:

- reusable orchestration
- domain-specific agents
- optional GenAI reasoning
- auditable traces for each action

## Limitations

- Uses synthetic/sample customer data only.
- Does not claim real churn accuracy.
- Does not estimate customer lifetime value or intervention ROI.
- Does not include production CRM integration.
- LLM outputs depend on configured providers or deterministic fallback behavior.

## Future Improvements

- Evaluate with labeled churn outcomes.
- Add customer segment-specific policies.
- Add uplift-based retention treatment selection.
- Add CRM integration and human approval steps.
- Monitor decision distribution, latency, and fallback behavior.
- Version retention policies, prompts, and rules.

