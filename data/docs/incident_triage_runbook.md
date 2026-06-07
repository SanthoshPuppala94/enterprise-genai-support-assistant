# Mock Incident Triage Runbook

This synthetic runbook models a generic enterprise correspondence support flow.
It contains no real company, client, customer, or production data.

## Missing Printed Correspondence

When business users report missing printed letters, support should verify:

1. Incident details and affected batch ID.
2. Batch job status on cloud-managed container batch workers.
3. PDF generation status.
4. Print file package status.
5. File handoff and downstream acknowledgement status.
6. Similar prior incidents and previous engineer actions.

## Operational Versus CR Decision

Operational issue indicators:

- PDF was generated successfully.
- File package was created.
- Failure is isolated to downstream acknowledgement or retryable handoff.
- Similar prior incidents were resolved by requeue or file transfer support.

CR candidate indicators:

- Template or rule mapping failure.
- Repeated failure with the same code path.
- Missing required paragraph, disclosure, or configuration mapping.
- Prior incidents required code/configuration change.

## Governance

The assistant may recommend next actions, but production reruns, customer-impacting
reprocessing, code changes, and CR creation require human approval. Every RCA
summary should include cited incident details, logs, prior resolutions, and
runbook guidance.

