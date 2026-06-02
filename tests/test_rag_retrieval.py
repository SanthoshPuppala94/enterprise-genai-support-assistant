from app.tools.rag_tools import search_documents


def test_rag_retrieves_mock_file_transfer_runbook():
    results = search_documents("file acknowledgement timeout remediation", k=2)
    assert results
    assert any("file_transfer_runbook.md" in result["source"] for result in results)
