from app.graph.state import ChatState
from app.services.guardrails import add_mock_data_disclaimer
from app.tools.sql_tools import SQLSafetyError, execute_select, question_to_sql


class SQLAgent:
    name = "sql_agent"

    def run(self, state: ChatState) -> ChatState:
        query = question_to_sql(state["question"])
        try:
            rows = execute_select(query)
            state["sql_results"] = rows
            state["answer"] = add_mock_data_disclaimer(
                f"Executed safe read-only SQL:\n\n```sql\n{query}\n```\n\n"
                f"Returned {len(rows)} row(s): {rows}"
            )
            state["citations"] = ["SQLite mock database: data/sql/schema.sql, data/sql/seed.sql"]
        except SQLSafetyError as exc:
            state["answer"] = f"SQL request rejected: {exc}"
            state["citations"] = []
        state["agent_used"] = self.name
        return state
