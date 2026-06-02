# Mock Correspondence File Transfer Runbook

This runbook is synthetic and intended for a GenAI interview PoC only.

## Common Issues

File acknowledgement timeout means the handoff job did not receive a mock
acknowledgement within the expected window. Operators should verify endpoint
availability, inspect retry counts, and requeue the batch when policy permits.

Template rule miss means a template could not resolve one or more paragraph
mappings. Operators should check the mock template code, policy version, and
rule configuration before rerunning.

PDF render warnings usually indicate missing optional assets. The batch may still
complete if required paragraphs and disclosures are present.

## Escalation

Escalate repeated timeouts, repeated template rule misses, or evidence of missing
mandatory disclosure text to the mock platform support queue.
