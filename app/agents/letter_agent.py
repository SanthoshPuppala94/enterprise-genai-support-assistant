from app.graph.state import ChatState
from app.tools.rag_tools import search_documents


SECTION_RULES = {
    "header": "Identifies mock recipient, template code, and print date.",
    "account summary": "Displays mock account context allowed by the communication policy.",
    "action required": "Maps to SOP rules for required customer action paragraphs.",
    "disclosure": "Maps to policy-controlled compliance text and retention requirements.",
}


class LetterExplanationAgent:
    name = "letter_agent"

    def run(self, state: ChatState) -> ChatState:
        docs = search_documents("letter template sections business rules disclosure action required", k=3)
        section_lines = [f"- {section.title()}: {rule}" for section, rule in SECTION_RULES.items()]
        state["answer"] = (
            "Mock printed letter output can be explained as these policy-driven sections:\n"
            + "\n".join(section_lines)
            + "\n\nEach section is traceable to mock SOP/template documentation and should never be treated as real client correspondence."
        )
        state["citations"] = [str(doc["source"]) for doc in docs]
        state["agent_used"] = self.name
        return state

