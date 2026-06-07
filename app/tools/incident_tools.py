import json
import re
from pathlib import Path
from typing import Any

from app.config import DATA_DIR, DOCS_DIR


INCIDENTS_PATH = DATA_DIR / "incidents" / "incidents.json"
PRINT_JOBS_PATH = DATA_DIR / "print_status" / "print_jobs.json"
RESOLUTIONS_PATH = DATA_DIR / "prior_resolutions" / "engineer_actions.json"
BATCH_LOG_DIR = DATA_DIR / "batch_logs"


def fetch_incident_details(incident_id: str) -> dict[str, Any]:
    incident_id = incident_id.upper().strip()
    for incident in _load_json(INCIDENTS_PATH):
        if incident["incident_id"].upper() == incident_id:
            return incident
    raise ValueError(f"Mock incident not found: {incident_id}")


def fetch_batch_job_logs(batch_id: str) -> dict[str, Any]:
    safe_batch_id = Path(batch_id.strip()).name
    path = BATCH_LOG_DIR / f"{safe_batch_id}.log"
    if not path.exists():
        raise ValueError(f"Mock batch log not found: {safe_batch_id}")
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = [line for line in lines if "STATUS=FAILED" in line or " ERROR " in line or " code=" in line]
    return {"batch_id": safe_batch_id, "source": str(path), "lines": lines, "signals": errors}


def fetch_print_delivery_status(print_job_id: str | None = None, batch_id: str | None = None) -> dict[str, Any]:
    for job in _load_json(PRINT_JOBS_PATH):
        if print_job_id and job["print_job_id"] == print_job_id:
            return job
        if batch_id and job["batch_id"] == batch_id:
            return job
    raise ValueError("Mock print delivery status not found")


def search_prior_resolutions(query: str) -> list[dict[str, Any]]:
    query_terms = {term.lower() for term in re.findall(r"[a-zA-Z0-9_]+", query) if len(term) > 2}
    matches = []
    for resolution in _load_json(RESOLUTIONS_PATH):
        text = json.dumps(resolution).lower()
        score = sum(1 for term in query_terms if term in text)
        if score:
            item = dict(resolution)
            item["score"] = score
            matches.append(item)
    return sorted(matches, key=lambda item: item["score"], reverse=True)


def search_incident_runbook(query: str) -> dict[str, str]:
    path = DOCS_DIR / "incident_triage_runbook.md"
    return {"source": str(path), "text": path.read_text(encoding="utf-8")}


def classify_resolution_path(
    incident: dict[str, Any],
    batch_logs: dict[str, Any],
    print_status: dict[str, Any],
    prior_resolutions: list[dict[str, Any]],
) -> dict[str, Any]:
    combined = " ".join(batch_logs.get("signals", [])).lower()
    if "template_rule_miss" in combined or "paragraph mapping" in combined:
        return {
            "path": "CR candidate",
            "cr_required": True,
            "reason": "Evidence points to template/rule mapping or recurring code/configuration behavior.",
        }
    if print_status.get("pdf_generated") and print_status.get("file_packaged") and not print_status.get(
        "downstream_acknowledged"
    ):
        return {
            "path": "Operational support action",
            "cr_required": False,
            "reason": "PDFs were generated and packaged, but downstream acknowledgement/file handoff failed.",
        }
    return {
        "path": "Insufficient evidence",
        "cr_required": False,
        "reason": "The available mock evidence does not isolate operational versus code/configuration cause.",
    }


def draft_cr_summary(incident_id: str) -> dict[str, str]:
    incident = fetch_incident_details(incident_id)
    return {
        "title": f"CR draft for {incident['incident_id']}: {incident['title']}",
        "summary": (
            f"Business impact: {incident['business_impact']}\n"
            f"Affected batch: {incident['batch_id']}\n"
            "Attach RCA evidence, failed log signals, prior incident matches, and regression test plan."
        ),
        "governance": "Draft only. Requires developer review, tests, approval, and no direct merge to protected branches.",
    }


def extract_incident_id(text: str) -> str | None:
    match = re.search(r"\bINC-\d{4}-\d{4}\b", text.upper())
    return match.group(0) if match else None


def _load_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))
