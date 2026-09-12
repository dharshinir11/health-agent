"""
RAG Knowledge Base Tool
Retrieves grounded information from approved healthcare documents
"""

import os
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag", "documents")


class RAGRetriever:
    """Document retriever with chunking and TF-IDF similarity search"""

    def __init__(self, docs_dir: str = DOCS_DIR, chunk_size: int = 500, chunk_overlap: int = 50):
        self.docs_dir = docs_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: TfidfVectorizer = None
        self.tfidf_matrix = None
        self._load_and_index()

    def _chunk_text(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks cleanly"""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        step = max(50, self.chunk_size - self.chunk_overlap)

        for para in paragraphs:
            if len(para) <= self.chunk_size:
                chunks.append({"text": para, "source": source})
            else:
                for start in range(0, len(para), step):
                    chunk = para[start:start + self.chunk_size].strip()
                    if chunk:
                        chunks.append({"text": chunk, "source": source})

        return chunks

    def _load_and_index(self):
        """Load all .txt files from docs_dir and build TF-IDF index"""
        self.chunks = []
        if not os.path.exists(self.docs_dir):
            return

        for filename in sorted(os.listdir(self.docs_dir)):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.docs_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        doc_chunks = self._chunk_text(content, filename)
                        self.chunks.extend(doc_chunks)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        if self.chunks:
            corpus = [c["text"] for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                lowercase=True
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 2, threshold: float = 0.08) -> Dict[str, Any]:
        """Search chunks matching query using cosine similarity"""
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return {
                "success": False,
                "answer": "I do not have that information in my approved documents.",
                "sources": [],
                "chunks": [],
                "top_score": 0.0
            }

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        top_indices = similarities.argsort()[::-1][:top_k]
        top_results = []
        sources = set()

        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                item = self.chunks[idx]
                top_results.append({
                    "text": item["text"],
                    "source": item["source"],
                    "score": round(score, 4)
                })
                sources.add(item["source"])

        if not top_results:
            return {
                "success": False,
                "answer": "I do not have that information in my approved documents.",
                "sources": [],
                "chunks": [],
                "top_score": float(similarities[top_indices[0]]) if len(top_indices) > 0 else 0.0
            }

        answer_parts = [r["text"] for r in top_results]
        answer = "\n\n".join(answer_parts)

        return {
            "success": True,
            "answer": answer,
            "sources": sorted(list(sources)),
            "chunks": top_results,
            "top_score": top_results[0]["score"]
        }


_retriever = None

def get_retriever() -> RAGRetriever:
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever

def search_knowledge_base(query: str, top_k: int = 2) -> Dict[str, Any]:
    """
    Search approved healthcare knowledge base documents for answers.
    """
    retriever = get_retriever()
    return retriever.search(query, top_k=top_k)
