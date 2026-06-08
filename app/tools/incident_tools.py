import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import DATA_DIR, DOCS_DIR


INCIDENTS_PATH = DATA_DIR / "incidents" / "incidents.json"
PRINT_JOBS_PATH = DATA_DIR / "print_status" / "print_jobs.json"
RESOLUTIONS_PATH = DATA_DIR / "prior_resolutions" / "engineer_actions.json"
BATCH_LOG_DIR = DATA_DIR / "batch_logs"
DEPLOYMENTS_PATH = DATA_DIR / "deployments" / "deployments.json"
COMMITS_PATH = DATA_DIR / "repo_history" / "commits.json"


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


def fetch_recent_deployments(before_timestamp: str, hours: int = 24) -> list[dict[str, Any]]:
    incident_time = _parse_utc(before_timestamp)
    matches = []
    for deployment in _load_json(DEPLOYMENTS_PATH):
        deployed_at = _parse_utc(deployment["deployed_at"])
        delta_hours = (incident_time - deployed_at).total_seconds() / 3600
        if 0 <= delta_hours <= hours:
            item = dict(deployment)
            item["hours_before_incident"] = round(delta_hours, 2)
            matches.append(item)
    return sorted(matches, key=lambda item: item["hours_before_incident"])


def search_repo_history(query: str) -> list[dict[str, Any]]:
    terms = {term.lower() for term in re.findall(r"[a-zA-Z0-9_]+", query) if len(term) > 2}
    matches = []
    for commit in _load_json(COMMITS_PATH):
        text = json.dumps(commit).lower()
        score = sum(1 for term in terms if term in text)
        if score:
            item = dict(commit)
            item["score"] = score
            matches.append(item)
    return sorted(matches, key=lambda item: item["score"], reverse=True)


def fetch_commit_details(commit_id: str) -> dict[str, Any]:
    commit_id = commit_id.strip().lower()
    for commit in _load_json(COMMITS_PATH):
        if commit["commit_id"].lower() == commit_id:
            return commit
    raise ValueError(f"Mock commit not found: {commit_id}")


def correlate_incident_with_code_changes(
    incident: dict[str, Any],
    batch_logs: dict[str, Any],
    window_hours: int = 24,
) -> dict[str, Any]:
    failed_module = _infer_failed_module(batch_logs)
    recent_deployments = fetch_recent_deployments(incident["reported_at"], hours=window_hours)
    related_deployments = [
        deployment
        for deployment in recent_deployments
        if failed_module in deployment.get("changed_modules", [])
    ]
    related_commits = search_repo_history(failed_module)
    confidence = "low"
    if related_deployments and related_commits:
        confidence = "medium"
    if related_deployments and any(failed_module == commit.get("module") for commit in related_commits):
        confidence = "high"
    return {
        "failed_module": failed_module,
        "recent_deployments": related_deployments,
        "related_commits": related_commits[:3],
        "confidence": confidence,
        "guardrail": (
            "Read-only correlation only. The assistant must not edit code, commit, push, merge, "
            "deploy, or bypass developer review and approval."
        ),
    }


def draft_code_change_analysis(incident_id: str) -> dict[str, str]:
    incident = fetch_incident_details(incident_id)
    logs = fetch_batch_job_logs(incident["batch_id"])
    correlation = correlate_incident_with_code_changes(incident, logs)
    commit_lines = [
        f"{commit['commit_id']} ({commit['committed_at']}): {commit['summary']}"
        for commit in correlation["related_commits"]
    ]
    return {
        "title": f"Code-change correlation for {incident_id}",
        "analysis": (
            f"Failed module: {correlation['failed_module']}\n"
            f"Correlation confidence: {correlation['confidence']}\n"
            f"Related commits: {'; '.join(commit_lines) if commit_lines else 'None found'}\n"
            "Recommended solution path: review the related module changes, reproduce with the failed batch, "
            "add regression coverage, and prepare a CR/PR only after developer validation."
        ),
        "guardrail": correlation["guardrail"],
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


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _infer_failed_module(batch_logs: dict[str, Any]) -> str:
    combined = " ".join(batch_logs.get("signals", [])).lower()
    if "file_handoff" in combined or "file_transfer_timeout" in combined:
        return "file_handoff_worker"
    if "template_rule_miss" in combined or "paragraph mapping" in combined:
        return "template_rule_engine"
    if "pdf_render" in combined:
        return "pdf_render_worker"
    return "correspondence_batch_worker"
