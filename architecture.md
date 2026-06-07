# Architecture

## Business Problem

Enterprise letter platforms often require support teams to answer questions
across workflow status, policies, SOPs, transfer runbooks, logs, and generated
letter output. This PoC models that support experience with mock data only. It is
inspired by regulated enterprise correspondence workflows and contains no real
company or client data.

## High-Level Architecture

The FastAPI app exposes `POST /chat`. A LangGraph supervisor receives the user
question, checks short-term state and stored preferences, then routes to one of
four agents:

- SQL Agent for mock operational database questions
- Document/RAG Agent for mock policies, SOPs, runbooks, and letter documentation
- Log Troubleshooting Agent for synthetic enterprise correspondence application logs
- Letter Explanation Agent for explaining mock printed letter output
- Incident RCA Agent for missing/delayed printed correspondence incidents

## Agent Flow

1. User posts `{ "question": "..." }` to `/chat`.
2. API loads long-term user preferences from SQLite.
3. LangGraph stores the question and routing decision in short-term state.
4. Supervisor chooses a specialist agent.
5. Specialist agent calls tools and returns an answer, selected agent, and citations.

## Incident RCA Flow

The incident workflow models support triage for business-reported missing printed
correspondence. It uses generic enterprise VM batch server terminology and mock
data only.

```text
INC ticket
   ↓
fetch_incident_details
   ↓
fetch_batch_job_logs from VM batch server logs
   ↓
fetch_print_delivery_status
   ↓
search_prior_resolutions
   ↓
search incident triage runbook
   ↓
classify operational support action vs CR candidate
   ↓
grounded RCA answer with citations
```

The assistant is positioned as support acceleration, not support replacement. It
helps engineers reuse previous incident knowledge and isolate the likely failure
area before taking action.

## MCP Integration

`app/mcp_server/server.py` is a production-style FastMCP server. Tools and
resources are registered with decorators so MCP clients can discover them at
runtime.

- Tools: `search_documents`, `execute_sql`, `analyze_logs`
- Resources: `mock://policies/enterprise-support`, `mock://runbooks/file-transfer`,
  `mock://letter-templates/generation-sop`

Incident RCA tools include `fetch_incident_details`, `fetch_batch_job_logs`,
`fetch_print_delivery_status`, `search_prior_resolutions`,
`classify_resolution_path`, and `draft_cr_summary`.

The server can be launched with `python -m app.mcp_server` and integrated with
an MCP-compatible host over stdio.

## RAG Flow

Mock markdown documents live in `data/docs`. The vector store service chunks the
documents and embeds them locally with a deterministic hash embedding fallback.
The RAG tool retrieves the highest scoring chunks and returns answer context with
source citations. The project includes ChromaDB in `requirements.txt` so the
local vector store can be swapped to persistent Chroma collections for larger
demos.

## SQL Flow

SQLite schema and seed files live in `data/sql`. `execute_select` initializes the
mock database and validates every query with `validate_select_only`. The guard
rejects INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, multi-statement SQL,
and any query that does not start with SELECT.

## Memory Design

Short-term memory is part of the LangGraph `ChatState`, including current
question, routing decision, citations, and interaction history. Long-term
preference memory is stored in the SQLite `user_preferences` table with
`response_style`, `preferred_agent`, and `preferred_detail_level`.

## API Key Handling

Secrets are loaded with `python-dotenv`. `.env.example` documents expected
variables, `.env` is ignored by git, and no API keys are hardcoded. The current
offline path works without a key; hosted OpenAI-compatible calls can be added
behind the existing configuration.

## Guardrails and Hallucination Controls

The assistant treats mock source grounding as a first-class requirement. RAG and
letter agents attach citations from local mock documents. If no citation is
available, the response is replaced with an evidence-limited fallback rather than
an unsupported answer.

SQL guardrails enforce SELECT-only access and block mutating, administrative, or
multi-statement SQL. All user-facing answers include a mock-data disclaimer so
demo output is not mistaken for real bank/client guidance.

Incident RCA guardrails require evidence from incident records, VM batch logs,
print delivery status, prior engineer actions, and runbooks. CR summaries are
draft-only and require human review, tests, approval, and standard change
governance before any implementation.

## Production Security Considerations

- Keep real client data out of local demos and test fixtures.
- Enforce least-privilege database credentials and read-only replicas for SQL agents.
- Use allow-listed query templates or SQL AST validation for higher assurance.
- Add authentication, authorization, request logging, and rate limits to FastAPI.
- Encrypt secrets with an enterprise vault instead of local `.env` files.
- Persist vector stores in controlled environments with document-level access checks.
- Add audit trails for agent routing decisions, tool calls, and retrieved citations.
- Apply prompt injection defenses for RAG content and tool arguments.
- Add human review before any generated letter content is sent downstream.
