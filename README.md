# 🏦 Enterprise GenAI Support Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-FF6B35?style=flat)](https://langchain-ai.github.io/langgraph/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain.com)
[![pytest](https://img.shields.io/badge/Tested_with-pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](LICENSE)

> **Production-style GenAI PoC** — A mock enterprise correspondence support assistant demonstrating LangGraph supervisor agents, RAG pipelines, SQL safety guardrails, MCP tool governance, and hallucination controls. Uses only synthetic data.

---

## What It Does

This assistant answers support queries for a mock banking letter-generation workflow. A **LangGraph supervisor agent** routes each incoming question to the right specialist:

| Agent | Responsibility |
|-------|---------------|
| **SQL Agent** | Queries operational data with SELECT-only safety validation |
| **RAG Agent** | Retrieves from mock policies, SOPs, and runbooks with citation grounding |
| **Log Agent** | Troubleshoots synthetic enterprise log signatures |
| **Letter Agent** | Explains printed letter sections and maps them to business rules |

All agents share short-term graph state and long-term SQLite preference memory.

---

## Architecture

```
POST /chat
    │
    ▼
LangGraph Supervisor
    │
    ├──► SQL Agent        → SELECT-only SQLite queries
    ├──► RAG Agent        → ChromaDB-style retrieval + citation check
    ├──► Log Agent        → Synthetic log pattern matching
    └──► Letter Agent     → SOP / letter section explanation
    │
    ▼
FastMCP Server (stdio)
    ├── Tools:     search_documents · execute_sql · analyze_logs
    └── Resources: mock://policies · mock://runbooks · mock://letter-templates
    │
    ▼
Response: { "answer": "...", "agent_used": "...", "citations": [...] }
```

---

## Key Design Decisions

- **Supervisor pattern** — Routes work to specialized agents instead of forcing one prompt to handle every task type
- **SQL guardrails** — Rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `PRAGMA`, and multi-statement SQL
- **Citation-grounded RAG** — Policy/SOP answers must cite mock documents; no citation → evidence-limited fallback
- **FastMCP decorators** — Tools and resources registered with explicit schemas so compatible clients can discover and govern them
- **Memory architecture** — Short-term graph state for the current session; SQLite for long-term user preferences
- **Secret hygiene** — All credentials via `.env`; no hardcoded API keys

---

## Getting Started

### Prerequisites
- Python 3.11+
- An OpenAI-compatible API key (optional — the PoC has deterministic local fallbacks for offline testing)

### Setup

```bash
git clone https://github.com/SanthoshPuppala94/enterprise-genai-support-assistant
cd enterprise-genai-support-assistant

python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key if using a hosted LLM
```

### Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

### Run the MCP Server

```bash
python -m app.mcp_server
```

### Run Tests

```bash
pytest
```

---

## Example Queries

```bash
# Query the database
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"question":"What failed letter batches are in the database?"}'

# Policy retrieval
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"question":"What does the enterprise support policy say about disclosure approval?"}'

# Log troubleshooting
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType "application/json" `
  -Body '{"question":"Troubleshoot the file transfer timeout from the logs."}'
```

### API Contract

**Request**
```json
{ "question": "Troubleshoot the file transfer timeout error in logs" }
```

**Response**
```json
{
  "answer": "Probable mock log findings...",
  "agent_used": "log_agent",
  "citations": ["data/logs/support_app.log"]
}
```

---

## Project Structure

```
enterprise-genai-support-assistant/
├── app/
│   ├── main.py           # FastAPI app + /chat endpoint
│   ├── agents/           # Supervisor + specialist agents
│   ├── mcp_server.py     # FastMCP tools and resources
│   └── memory.py         # Short-term + SQLite long-term memory
├── data/                 # Synthetic mock data (policies, logs, letters)
├── tests/                # pytest test suite
├── architecture.md       # Architecture detail and design decisions
├── .env.example          # Environment template
└── requirements.txt
```

---

## ⚠️ Data Notice

This project uses **only synthetic data**. It does not contain real company, client, customer, account, letter, log, or production system data of any kind.

---

## About

Built as a portfolio project to demonstrate enterprise GenAI patterns — not a production deployment. Talking points:

- Supervisor routing vs. monolithic prompting
- SQL guardrails for safe operational data access
- Citation-grounded RAG for auditability
- MCP tool governance with FastMCP
- Memory without hiding state in prompt text
- Hallucination controls through evidence-limited fallbacks
