# Enterprise GenAI Support Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-green?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Workflow-purple?style=flat)](https://www.langchain.com/langgraph)
[![MCP](https://img.shields.io/badge/MCP-Tool%20Server-orange?style=flat)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen?style=flat)](https://docs.pytest.org/)

> **Production-style GenAI PoC** — A mock enterprise correspondence support assistant demonstrating LangGraph supervisor agents, MCP tool governance, incident RCA, RAG, SQL safety guardrails, memory, and hallucination controls. Uses only synthetic data.

---

## What It Does

This assistant models a realistic enterprise support workflow where business users raise incidents when expected printed correspondence is missing or delayed. It helps reduce repetitive incident triage by retrieving mock incident details, cloud/container batch worker logs, PDF/print delivery status, prior engineer actions, and runbook guidance before recommending next steps.

A **LangGraph supervisor agent** routes each incoming question to the right specialist:

| Agent | Responsibility |
|-------|---------------|
| **Incident RCA Agent** | Investigates missing/delayed printed correspondence incidents |
| **SQL Agent** | Queries operational data with SELECT-only safety validation |
| **Document/RAG Agent** | Searches policies, SOPs, runbooks, and letter documentation |
| **Log Troubleshooting Agent** | Analyzes synthetic application logs |
| **Letter Explanation Agent** | Explains mock printed letter output and business rules |

---

## Incident RCA Workflow

```text
Business incident
   ↓
LangGraph supervisor
   ↓
Incident RCA Agent
   ↓
MCP tools fetch:
   - incident details
   - cloud/container batch worker logs
   - PDF/print delivery status
   - prior engineer resolutions
   - incident triage runbook
   ↓
Grounded RCA:
   - confirmed facts
   - probable failure area
   - previous engineer actions
   - operational vs CR recommendation
   - citations and guardrail note
```

The infrastructure is modeled as **Dockerized batch workers running in a cloud-ready enterprise environment**. The project stays provider-neutral, but the terminology aligns with modern containerized workloads, centralized logging, and cloud deployment patterns.

---

## MCP Tools and Resources

Decorated FastMCP tools:

- `search_documents`
- `execute_sql`
- `analyze_logs`
- `fetch_incident_details`
- `fetch_batch_job_logs`
- `fetch_print_delivery_status`
- `search_prior_resolutions`
- `classify_resolution_path`
- `draft_cr_summary`

Decorated FastMCP resources:

- `mock://policies/enterprise-support`
- `mock://runbooks/file-transfer`
- `mock://letter-templates/generation-sop`
- `mock://runbooks/incident-triage`

---

## Guardrails, Hallucination Controls, and Governance

- SQL tools are SELECT-only and reject INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, and multi-statement SQL.
- RAG and incident RCA answers include citations from mock documents, logs, incidents, or runbooks.
- If citations are unavailable, the assistant returns an evidence-limited fallback instead of inventing a source.
- Responses include a mock-data disclaimer so generated answers are not confused with real enterprise guidance.
- Incident recommendations separate confirmed facts, probable root cause, prior engineer actions, and CR decision.
- CR guidance is draft-only; no automated merge, deployment, rerun, or production reprocessing is allowed.
- Human approval is required before rerun, reprocess, CR creation, code change, or customer-impacting action.

---

## Tech Stack

- Python 3.11+
- FastAPI
- LangGraph
- LangChain-compatible structure
- FastMCP
- SQLite
- Local vector search with deterministic embeddings and Chroma-compatible path
- pytest
- python-dotenv

---

## Setup

```powershell
cd enterprise-genai-support-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` only if you want to add an OpenAI-compatible API key. The current implementation runs offline with deterministic mock data.

---

## Run Locally

```powershell
uvicorn app.main:app --reload --port 8000
```

Run the MCP server over stdio:

```powershell
python -m app.mcp_server
```

---

## Example Queries

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"question":"Why did INC-2026-1042 happen and does it need a CR?"}'
```

Other sample questions:

- What failed letter batches are in the database?
- What does the mock enterprise support policy say about disclosure approval?
- Troubleshoot the file transfer timeout from the logs.
- Explain the printed letter sections and the business rules behind them.
- Business says printed letters were not received. What should support check?
- What actions did previous engineers take for similar incidents?
- Does INC-2026-1042 need a CR or can support resolve it operationally?

---

## API Contract

`POST /chat`

Request:

```json
{ "question": "Why did INC-2026-1042 happen and does it need a CR?" }
```

Response:

```json
{
  "answer": "Incident RCA summary...",
  "agent_used": "incident_agent",
  "citations": ["incident:INC-2026-1042", "data/batch_logs/B-1002.log"]
}
```

---

## Run Tests

```powershell
pytest
```

---

## Data Notice

This project uses **only synthetic data**. It does not contain real company, client, customer, account, letter, log, incident, or production system data of any kind.

---

## Interview Positioning

Say:

> “I built a mock enterprise correspondence support assistant to reduce repetitive incident triage. When business users report missing printed letters, the assistant uses MCP tools to fetch incident details, cloud/container batch logs, print delivery status, prior engineer actions, and runbook guidance. A LangGraph RCA workflow then produces a grounded summary with citations and recommends whether support can resolve it operationally or whether a CR is needed.”

Strong talking points:

- Supervisor agent routes to specialized agents.
- MCP acts as a governed integration layer for logs, incident records, prior resolutions, and runbooks.
- RCA is grounded in evidence and citations to reduce hallucinations.
- Prior engineer actions reduce dependency on tribal knowledge.
- SQL and MCP tools are constrained and auditable.
- CR recommendations are draft-only and require human review, tests, approvals, and standard governance.
