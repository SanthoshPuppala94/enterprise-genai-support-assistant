from pathlib import Path

from app.config import LOGS_DIR


ISSUE_PATTERNS = {
    "LCD_FILE_TIMEOUT": {
        "root_cause": "Outbound LCD file handoff exceeded the configured acknowledgement window.",
        "remediation": "Validate the transfer endpoint, retry the batch, and notify operations if acknowledgements remain delayed.",
    },
    "TEMPLATE_RULE_MISS": {
        "root_cause": "A letter template rule could not resolve a required paragraph mapping.",
        "remediation": "Review template-to-policy mappings and reprocess affected mock letters after correction.",
    },
    "PDF_RENDER_WARN": {
        "root_cause": "The print rendering service detected a missing optional asset.",
        "remediation": "Confirm mock template assets are present; rendering can continue if the section is optional.",
    },
}


def analyze_logs(log_path: Path | None = None) -> dict[str, object]:
    path = log_path or LOGS_DIR / "lws_app.log"
    content = path.read_text(encoding="utf-8")
    findings = []
    for code, detail in ISSUE_PATTERNS.items():
        if code in content:
            findings.append({"code": code, **detail})
    return {
        "log_file": str(path),
        "findings": findings,
        "line_count": len(content.splitlines()),
    }

