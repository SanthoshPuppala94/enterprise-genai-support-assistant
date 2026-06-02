from app.services.guardrails import (
    MOCK_DATA_DISCLAIMER,
    add_mock_data_disclaimer,
    apply_grounding_guardrails,
)


def test_guardrail_adds_mock_data_disclaimer():
    answer = add_mock_data_disclaimer("Mock answer")
    assert MOCK_DATA_DISCLAIMER in answer


def test_grounding_guardrail_blocks_uncited_answer():
    answer = apply_grounding_guardrails("Unsupported claim", [])
    assert "do not have enough grounded mock-source evidence" in answer
    assert MOCK_DATA_DISCLAIMER in answer

