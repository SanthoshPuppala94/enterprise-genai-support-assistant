from app.graph.state import ChatState
from app.services.guardrails import add_mock_data_disclaimer
from app.tools.log_tools import analyze_logs


class LogTroubleshootingAgent:
    name = "log_agent"

    def run(self, state: ChatState) -> ChatState:
        analysis = analyze_logs()
        findings = analysis["findings"]
        if not findings:
            answer = "No known mock LWS/LCD issue signatures were found in the application log."
        else:
            lines = []
            for finding in findings:
                lines.append(
                    f"- {finding['code']}: {finding['root_cause']} Remediation: {finding['remediation']}"
                )
            answer = "Probable mock log findings:\n" + "\n".join(lines)
        state["answer"] = add_mock_data_disclaimer(answer)
        state["citations"] = [str(analysis["log_file"])]
        state["agent_used"] = self.name
        return state
