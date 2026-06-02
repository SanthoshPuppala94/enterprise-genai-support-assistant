import pytest

from app.tools.sql_tools import SQLSafetyError, execute_select, validate_select_only


def test_select_query_is_allowed(tmp_path):
    assert validate_select_only("SELECT * FROM letter_batches") == "SELECT * FROM letter_batches"


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM letter_batches",
        "UPDATE letter_batches SET status = 'DONE'",
        "DROP TABLE letter_batches",
        "SELECT * FROM letter_batches; DELETE FROM letter_batches",
    ],
)
def test_mutating_queries_are_rejected(query):
    with pytest.raises(SQLSafetyError):
        validate_select_only(query)


def test_execute_select_returns_structured_rows(tmp_path):
    rows = execute_select("SELECT batch_id, status FROM letter_batches ORDER BY batch_id", db_path=tmp_path / "test.db")
    assert rows
    assert {"batch_id", "status"}.issubset(rows[0])

