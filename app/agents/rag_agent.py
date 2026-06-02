from app.graph.state import ChatState
from app.tools.rag_tools import search_documents


class DocumentRAGAgent:
    name = "rag_agent"

    def run(self, state: ChatState) -> ChatState:
        results = search_documents(state["question"], k=3)
        citations = [str(result["source"]) for result in results]
        context = "\n\n".join(f"[{result['source']}] {result['text']}" for result in results)
        state["answer"] = (
            "Based on the mock enterprise documentation, the relevant guidance is:\n\n"
            f"{context}\n\n"
            "Use this as PoC guidance only; it is not real client or bank policy."
        )
        state["citations"] = citations
        state["agent_used"] = self.name
        return state

