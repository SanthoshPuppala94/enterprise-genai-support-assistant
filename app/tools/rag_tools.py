from app.services.vector_store import LocalVectorStore


def search_documents(question: str, k: int = 4) -> list[dict[str, str | float]]:
    store = LocalVectorStore()
    store.ensure_index()
    return store.search(question, k=k)

