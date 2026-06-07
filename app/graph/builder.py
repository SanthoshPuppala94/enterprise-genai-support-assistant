from langgraph.graph import END, StateGraph

from app.agents.incident_agent import IncidentRCAAgent
from app.agents.letter_agent import LetterExplanationAgent
from app.agents.log_agent import LogTroubleshootingAgent
from app.agents.rag_agent import DocumentRAGAgent
from app.agents.sql_agent import SQLAgent
from app.graph.state import ChatState
from app.graph.supervisor import route_question
from app.memory.preference_store import PreferenceStore


def build_graph(preference_store: PreferenceStore):
    sql_agent = SQLAgent()
    rag_agent = DocumentRAGAgent()
    log_agent = LogTroubleshootingAgent()
    letter_agent = LetterExplanationAgent()
    incident_agent = IncidentRCAAgent()

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

    def run_incident(state: ChatState) -> ChatState:
        return incident_agent.run(state)

    workflow = StateGraph(ChatState)
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("sql_agent", run_sql)
    workflow.add_node("rag_agent", run_rag)
    workflow.add_node("log_agent", run_logs)
    workflow.add_node("letter_agent", run_letter)
    workflow.add_node("incident_agent", run_incident)
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["agent_used"],
        {
            "sql_agent": "sql_agent",
            "rag_agent": "rag_agent",
            "log_agent": "log_agent",
            "letter_agent": "letter_agent",
            "incident_agent": "incident_agent",
        },
    )
    for node in ("sql_agent", "rag_agent", "log_agent", "letter_agent", "incident_agent"):
        workflow.add_edge(node, END)
    return workflow.compile()
