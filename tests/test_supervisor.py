from app.graph.supervisor import route_question


def test_supervisor_routes_sql_question():
    assert route_question({"question": "Show failed batch status"}) == "sql_agent"


def test_supervisor_routes_log_question():
    assert route_question({"question": "Troubleshoot the LCD timeout error in logs"}) == "log_agent"


def test_supervisor_routes_letter_question():
    assert route_question({"question": "Explain the printed letter sections"}) == "letter_agent"


def test_supervisor_honors_preferred_agent():
    assert (
        route_question(
            {
                "question": "What does the policy say?",
                "preferences": {"preferred_agent": "sql_agent"},
            }
        )
        == "sql_agent"
    )

