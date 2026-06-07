from app.tools.incident_tools import (
    classify_resolution_path,
    fetch_batch_job_logs,
    fetch_incident_details,
    fetch_print_delivery_status,
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

