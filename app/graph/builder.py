from langgraph.graph import END, StateGraph

from app.agents.letter_agent import LetterExplanationAgent
from app.agents.log_agent import LogTroubleshootingAgent
from app.agents.rag_agent import DocumentRAGAgent
from app.agents.sql_agent import SQLAgent
from app.graph.state import ChatState
from app.graph.incident_workflow import IncidentRCAWorkflow
from app.graph.supervisor import route_question
from app.memory.preference_store import PreferenceStore


def build_graph(preference_store: PreferenceStore):
    sql_agent = SQLAgent()
    rag_agent = DocumentRAGAgent()
    log_agent = LogTroubleshootingAgent()
    letter_agent = LetterExplanationAgent()
    incident_workflow = IncidentRCAWorkflow()

    def supervisor(state: ChatState) -> ChatState:
        state["agent_used"] = route_question(state)
        state["history"] = state.get("history", []) + [
            {"role": "user", "content": state["question"]},
            {"role": "supervisor", "content": f"Routed to {state['agent_used']}"},
        ]
        return state

    def run_sql(state: ChatState) -> ChatState:
        return sql_agent.run(state)

    def run_rag(state: ChatState) -> ChatState:
        return rag_agent.run(state)

    def run_logs(state: ChatState) -> ChatState:
        return log_agent.run(state)

    def run_letter(state: ChatState) -> ChatState:
        return letter_agent.run(state)

    workflow = StateGraph(ChatState)
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("sql_agent", run_sql)
    workflow.add_node("rag_agent", run_rag)
    workflow.add_node("log_agent", run_logs)
    workflow.add_node("letter_agent", run_letter)
    workflow.add_node("incident_intake", incident_workflow.intake)
    workflow.add_node("incident_fetch_details", incident_workflow.fetch_incident)
    workflow.add_node("incident_fetch_batch_logs", incident_workflow.fetch_batch_logs)
    workflow.add_node("incident_fetch_print_status", incident_workflow.fetch_print_status)
    workflow.add_node("incident_search_prior_resolutions", incident_workflow.search_prior_resolutions)
    workflow.add_node("incident_search_runbook", incident_workflow.search_runbook)
    workflow.add_node("incident_correlate_code_changes", incident_workflow.correlate_code_changes)
    workflow.add_node("incident_classify_resolution", incident_workflow.classify_resolution)
    workflow.add_node("incident_finalize", incident_workflow.finalize)
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["agent_used"],
        {
            "sql_agent": "sql_agent",
            "rag_agent": "rag_agent",
            "log_agent": "log_agent",
            "letter_agent": "letter_agent",
            "incident_agent": "incident_intake",
        },
    )
    workflow.add_edge("incident_intake", "incident_fetch_details")
    workflow.add_edge("incident_fetch_details", "incident_fetch_batch_logs")
    workflow.add_edge("incident_fetch_batch_logs", "incident_fetch_print_status")
    workflow.add_edge("incident_fetch_print_status", "incident_search_prior_resolutions")
    workflow.add_edge("incident_search_prior_resolutions", "incident_search_runbook")
    workflow.add_edge("incident_search_runbook", "incident_correlate_code_changes")
    workflow.add_edge("incident_correlate_code_changes", "incident_classify_resolution")
    workflow.add_edge("incident_classify_resolution", "incident_finalize")
    workflow.add_edge("incident_finalize", END)
    for node in ("sql_agent", "rag_agent", "log_agent", "letter_agent"):
        workflow.add_edge(node, END)
    return workflow.compile()
