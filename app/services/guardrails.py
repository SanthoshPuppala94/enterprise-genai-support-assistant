MOCK_DATA_DISCLAIMER = (
    "This answer is based only on synthetic mock data and mock documentation. "
    "It must not be treated as real bank, client, customer, or production guidance."
)


def require_citations(answer: str, citations: list[str]) -> str:
    if citations:
        return answer
    return (
        "I do not have enough grounded mock-source evidence to answer confidently. "
        "Please provide or index the relevant mock document, log, or database source."
    )


def add_mock_data_disclaimer(answer: str) -> str:
    if MOCK_DATA_DISCLAIMER in answer:
        return answer
    return f"{answer}\n\nGuardrail note: {MOCK_DATA_DISCLAIMER}"


def apply_grounding_guardrails(answer: str, citations: list[str]) -> str:
    grounded = require_citations(answer, citations)
    return add_mock_data_disclaimer(grounded)

