# Product direction: evidence-led security assessment operations

**Owner direction recorded 2026-09-21. This is an engineering product direction, not an implemented-feature list, patent/novelty claim, release commitment or investor forecast.** Current functionality is in README.md; measured progress is in PROGRESS.md.

## The product, not the model, owns the workflow

Aim to help an authorized assessment team manage the journey from engagement and scope to observations, controlled verification, remediation, retesting and handover. Ollama is the current gateway; users may choose local or cloud-backed models under a clear data-processing policy. Evidence schemas, tool authority and test outcomes do not depend on model brand, size or location. Local hardware is an economic/deployment option to measure later, not a requirement imposed on the owner during this sprint.

The product should reduce operator effort while making every conclusion more auditable. It must not claim to replace all expertise, legal judgment or customer-specific review. Global reputation is an outcome others may grant, not a feature the code can guarantee.

## Target end-to-end engagement journey (mostly planned)

1. Record customer, approved assets, exclusions, test accounts, time window, effects, request budgets, data handling and stop contact. Preview exactly what the proposed run may do.
2. Inspect the project's code/configuration/dependencies and scoped web/API surfaces through reviewed adapters. Keep failed, excluded, unsupported and executed coverage distinct.
3. Triage observations by evidence, confidence, technical severity, assumptions and business context, rather than a single invented safety score.
4. Demonstrate the relevant impact with the smallest approved, non-destructive proof. Use synthetic records/canaries or customer-designated test data. Stop after sufficient evidence; deeper access is not an objective in itself.
5. Supply evidence-linked remediation and independently recheck it under comparable coverage. Separate fixed, not reproduced, not retested and regression.
6. Produce a reviewed executive summary and detailed technical appendix with scope, method versions, evidence, demonstrated impact, limitations, remediation and residual work.

An authorization checkbox does not grant unrestricted access. No autonomous persistence, credential theft, real-data extraction, lateral movement or open-ended compromise agent is part of this direction. The current code's only practical authorization proof is in the disposable owned fixture, not external customer systems.

## High-value differentiators to test, not unsupported novelty claims

| Candidate | User value | Acceptance evidence | Current state |
|---|---|---|---|
| Coverage-aware retest | Prevents a broken scanner from falsely marking a vulnerability fixed. | Regression fixtures distinguish fixed, skipped, changed scope and not reproduced. | Planned; statuses exist but cross-run matching is not implemented. |
| Evidence replay bundle | Lets another reviewer follow a finding without repeating risky actions. | Versioned inputs, safe evidence, tool IDs and integrity checks reproduce the interpretation. | Report hashes/exports exist; CI source review bundle added; finding replay pending. |
| Permission and effect preview | Shows requests, role contexts and excluded assets before execution. | Planner output cannot exceed the independently enforced scope/action registry. | Basic scope/approval exists; full preview pending. |
| Role-difference matrix | Makes access-control failures understandable across designated test roles. | Owned vulnerable/fixed fixtures with independent denied controls and no real records. | One synthetic canary exists; matrix pending. |
| Knowledge provenance and freshness | Shows which dated source supports advice, including uncertainty. | Source revisions, licensing, conflict tests, evaluation and rollback. | Planned; no automatic updater or training runs exist. |
| Comparable model budget view | Helps choose hardware/models from measured usefulness and resource usage. | Labeled known/unknown token counters, fixed evaluation cases, measured latency and memory. | Protocol usage added; real model/hardware benchmarking pending. |

## Knowledge updates are not model self-training

A first implementation should refresh approved documentation/advisory records into a retrieval index with source URLs, licenses, versions and dates. Retrieve only relevant passages for an assessment; do not ingest the internet indiscriminately or let retrieved instructions control tools. Keep each customer's private evidence isolated from shared knowledge and require a new review for broader external disclosure.

Embeddings/RAG and actual weight changes are different mechanisms. Fine-tuning or swapping a model/adapter requires a separately reviewed training source, held-out tests, deployment approval and rollback. The application should never rewrite its own executable code, permissions or model weights merely because it retrieved a new article.

Primary implementation references: https://docs.ollama.com/capabilities/embeddings and https://docs.ollama.com/import . Neither facility is integrated here yet.

## Readiness gates for wider review

Favor a small reproducible release over a long feature list: vulnerable/fixed fixture coverage, honest failure paths, cancellation/deadline guarantees, crash recovery, reviewed adapter licensing, cross-platform installation checks, real-model compatibility, accessible browser E2E, privacy review and independently reviewable sample reports. Prepare an upstream proposal from tested contributions; submission and maintainer acceptance are separate events. Do not promise an investment, number of stars or global-market position by the sprint end.
