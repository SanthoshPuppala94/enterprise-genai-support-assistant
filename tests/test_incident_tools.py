from app.tools.incident_tools import (
    classify_resolution_path,
    correlate_incident_with_code_changes,
    fetch_batch_job_logs,
    fetch_commit_details,
    fetch_incident_details,
    fetch_print_delivery_status,
    fetch_recent_deployments,
    search_repo_history,
    search_prior_resolutions,
)


def test_fetch_incident_details():
    incident = fetch_incident_details("INC-2026-1042")
    assert incident["batch_id"] == "B-1002"
    assert incident["print_job_id"] == "P-7781"


def test_fetch_batch_job_logs_returns_failed_signals():
    logs = fetch_batch_job_logs("B-1002")
    assert logs["signals"]
    assert any("FILE_TRANSFER_TIMEOUT" in line for line in logs["signals"])


def test_classify_operational_resolution_path():
    incident = fetch_incident_details("INC-2026-1042")
    logs = fetch_batch_job_logs(incident["batch_id"])
    status = fetch_print_delivery_status(batch_id=incident["batch_id"])
    prior = search_prior_resolutions("file acknowledgement timeout")
    result = classify_resolution_path(incident, logs, status, prior)
    assert result["path"] == "Operational support action"
    assert not result["cr_required"]


def test_code_change_correlation_finds_recent_deployment_and_commit():
    incident = fetch_incident_details("INC-2026-1042")
    logs = fetch_batch_job_logs(incident["batch_id"])
    correlation = correlate_incident_with_code_changes(incident, logs)
    assert correlation["failed_module"] == "file_handoff_worker"
    assert correlation["confidence"] == "high"
    assert correlation["recent_deployments"]
    assert correlation["related_commits"]
    assert "must not edit code" in correlation["guardrail"]


def test_read_only_repo_history_tools():
    deployments = fetch_recent_deployments("2026-05-17T10:30:00Z", hours=24)
    commits = search_repo_history("file_handoff_worker timeout")
    commit = fetch_commit_details("c0ffee1")
    assert deployments[0]["deployment_id"] == "DEP-2026-0517-01"
    assert commits[0]["module"] == "file_handoff_worker"
    assert commit["linked_cr"] == "CR-2026-2201"

