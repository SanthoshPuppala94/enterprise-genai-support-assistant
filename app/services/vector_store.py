import math
from dataclasses import dataclass

from app.config import DOCS_DIR, ROOT_DIR
from app.services.embeddings import HashEmbedding


@dataclass
class Chunk:
    source: str
    text: str
    embedding: list[float]


class LocalVectorStore:
    def __init__(self):
        self.embedding_model = HashEmbedding()
        self._chunks: list[Chunk] = []
        self._chroma_collection = None

    def ensure_index(self) -> None:
        if self._chunks or self._chroma_collection is not None:
            return
        raw_chunks: list[tuple[str, str]] = []
        for path in sorted(DOCS_DIR.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for idx, chunk in enumerate(self._split(text)):
                source = f"{path.name}#chunk-{idx + 1}"
                raw_chunks.append((source, chunk))
        if self._try_chroma(raw_chunks):
            return
        self._chunks = [
            Chunk(source=source, text=text, embedding=self.embedding_model.embed_query(text))
            for source, text in raw_chunks
        ]

    def search(self, query: str, k: int = 4) -> list[dict[str, str | float]]:
        self.ensure_index()
        if self._chroma_collection is not None:
            results = self._chroma_collection.query(
                query_embeddings=[self.embedding_model.embed_query(query)],
                n_results=k,
            )
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            return [
                {
                    "source": metadata["source"],
                    "text": document,
                    "score": 1.0 / (1.0 + distance),
                }
                for document, metadata, distance in zip(documents, metadatas, distances)
            ]
        query_embedding = self.embedding_model.embed_query(query)
        scored = [
            {
                "source": chunk.source,
                "text": chunk.text,
                "score": self._cosine(query_embedding, chunk.embedding),
            }
            for chunk in self._chunks
        ]
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:k]

    def _try_chroma(self, raw_chunks: list[tuple[str, str]]) -> bool:
        try:
            import chromadb
        except ImportError:
            return False

        client = chromadb.PersistentClient(path=str(ROOT_DIR / "data" / "chroma"))
        collection = client.get_or_create_collection("mock_lws_docs")
        existing = collection.count()
        if existing == 0 and raw_chunks:
            ids = [source for source, _ in raw_chunks]
            texts = [text for _, text in raw_chunks]
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=self.embedding_model.embed_documents(texts),
                metadatas=[{"source": source} for source, _ in raw_chunks],
            )
        self._chroma_collection = collection
        return True

    @staticmethod
    def _split(text: str, max_words: int = 90) -> list[str]:
        words = text.split()
        return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        return sum(a * b for a, b in zip(left, right)) / (
            math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right)) or 1.0
        )
