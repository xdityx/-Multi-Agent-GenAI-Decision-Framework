# Limitations

## Summary

This project is a recruiter-friendly and interview-useful demonstration of multi-agent decision orchestration. It is intentionally scoped as an explainable system design project, not as a production decision engine or trained predictive ML model.

## Data Limitations

- The project uses synthetic/sample data.
- Customer IDs and transaction IDs are generated for demos.
- RAG documents are small sample policy documents.
- There are no real labels for churn, fraud, payment approval, chargebacks, or retention outcomes.
- There is no claim of real-world prediction accuracy.

## Modeling Limitations

- The system is not a trained predictive ML model.
- Heuristic rules are simple and demonstration-oriented.
- Decision scores are workflow signals, not calibrated probabilities.
- LLM output can vary by provider, model, prompt, and configuration.
- Mock fallback behavior is useful for local tests but is not model validation.

## Product And Production Limitations

- No production authentication or authorization.
- No persistent audit database.
- No queueing or human review workflow.
- No model monitoring, data drift monitoring, or alerting.
- No compliance sign-off process.
- No production deployment hardening.
- No real-time service-level guarantees.

## Domain Limitations

### Payments

- No real payment outcomes or chargeback labels.
- No payment network integration.
- No compliance workflow for payment operations.

### Churn

- No real churn labels or retention outcome measurement.
- No CRM integration.
- No uplift modeling or treatment optimization.

### Fraud

- No real fraud labels or investigator feedback.
- No case management integration.
- No real-time fraud enforcement path.

## Responsible Interpretation

The project should be described as:

- an explainable decision orchestration framework
- a multi-agent GenAI architecture demo
- a portfolio project showing API, dashboard, tests, and agent traces
- a foundation that could be extended with real data and production controls

The project should not be described as:

- production-ready
- a validated fraud detection system
- a validated churn prediction system
- a real payment risk model
- a replacement for compliance, risk, or human review processes

## Future Improvements

- Add real labeled datasets for offline evaluation.
- Add persistence for decisions and traces.
- Add auth, rate limiting, and secure configuration management.
- Add human-in-the-loop review.
- Add monitoring for latency, fallback usage, and decision distributions.
- Add versioning for agents, rules, prompts, and policy documents.

