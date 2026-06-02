# Mock Letter Generation SOP

This SOP describes a mock enterprise correspondence generation process. It is
not a real bank procedure and contains no real client data.

## Workflow

1. Intake receives a mock event from an upstream servicing system.
2. The rule engine selects a template and required paragraphs.
3. The renderer creates a sample PDF-ready payload.
4. The file transfer job packages the output for downstream print simulation.
5. Operations reviews failed batches and restarts eligible jobs.

## Letter Sections

The header includes mock recipient and template information. The account summary
uses synthetic account context. The action required section explains the customer
response expected by the mock scenario. The disclosure section maps to approved
policy text and must remain version controlled.

## Quality Checks

Generated letters should be validated for template version, paragraph order,
required disclosure, and transfer status before they are marked complete.
