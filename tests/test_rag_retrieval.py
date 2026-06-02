from app.tools.rag_tools import search_documents


def test_rag_retrieves_mock_lcd_runbook():
    results = search_documents("LCD file acknowledgement timeout remediation", k=2)
    assert results
    assert any("lcd_file_transfer_runbook.md" in result["source"] for result in results)

