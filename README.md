# Enterprise GenAI Support Assistant

Enterprise GenAI Support Assistant is a mock production-style GenAI PoC inspired
by enterprise correspondence support workflows. It uses only synthetic data and
does not contain real company, client, customer, account, letter, log, or
production system data.

## What It Demonstrates

- LangGraph supervisor agent that routes requests to specialist agents
- SQLite SQL agent with SELECT-only safety validation
- Document/RAG agent over mock policies, SOPs, runbooks, and letter docs
- Log troubleshooting agent for synthetic enterprise correspondence issue signatures
- Letter explanation agent that maps mock printed output sections to policies
- Short-term state memory in LangGraph and long-term preference memory in SQLite
- Production-style FastMCP server with decorated tools and resources
- FastAPI `/chat` endpoint for local demos
- Guardrails for SQL safety, mock-data boundaries, citation grounding, and hallucination control

## Setup

```powershell
cd enterprise-genai-support-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and add an OpenAI-compatible API key only if you want to extend the
PoC with hosted LLM calls. The current implementation has deterministic local
fallbacks for offline testing.

## Run Locally

```powershell
uvicorn app.main:app --reload --port 8000
```

Run the MCP server over stdio:

```powershell
python -m app.mcp_server
```

The MCP server registers these decorated tools:

- `search_documents`
- `execute_sql`
- `analyze_logs`

It also registers these decorated resources:

- `mock://policies/enterprise-support`
- `mock://runbooks/file-transfer`
- `mock://letter-templates/generation-sop`

Then call:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"question":"What failed letter batches are in the database?"}'
```

## Run Tests

```powershell
pytest
```

## Sample Questions

- What failed letter batches are in the database?
- What does the mock enterprise support policy say about disclosure approval?
- Troubleshoot the file transfer timeout from the logs.
- Explain the printed letter sections and the business rules behind them.
- Show customer communication preferences from the mock database.

## API Contract

`POST /chat`

Request:

```json
{ "question": "Troubleshoot the file transfer timeout error in logs" }
```

Response:

```json
{
  "answer": "Probable mock log findings...",
  "agent_used": "log_agent",
  "citations": ["data/logs/support_app.log"]
}
```

## Guardrails and Hallucination Controls

- SQL tools are SELECT-only and reject INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, and multi-statement SQL.
- RAG and letter explanations require citations from mock documents before returning grounded answers.
- Responses include a mock-data disclaimer so generated answers are not confused with real banking/client guidance.
- If citations are unavailable, the assistant returns an evidence-limited fallback instead of inventing a source.
- Secrets are loaded through `.env`; API keys are never hardcoded.

## Interview Positioning

Say this is a safe, mock production-style GenAI PoC for enterprise
correspondence support. It mirrors the patterns of regulated enterprise support
workflows without using any real company or client data. The strongest talking
points are:

- You used a supervisor pattern to route work to specialized agents instead of
  forcing one prompt to handle every task.
- You added SQL guardrails so the agent can query operational data but cannot
  mutate the database.
- You used RAG with citations so policy/SOP answers remain grounded in approved
  mock documents.
- You registered MCP tools/resources with `FastMCP` decorators so compatible
  clients can discover and execute the same governed capabilities.
- You included memory for user preferences while keeping sensitive data out of
  the demo.
- You documented security considerations such as secrets handling, SQL safety,
  least privilege, auditability, and mock-data boundaries.
- You added hallucination controls through citations, evidence-limited fallback
  responses, and explicit mock-data guardrail notes.
