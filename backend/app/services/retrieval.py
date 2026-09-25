import os
import json
import re
from typing import List, Dict, Any, Optional
from app.config import settings


class DocumentStore:
    def __init__(self, documents_dir: Optional[str] = None):
        self.documents_dir = documents_dir or os.path.join(settings.DATA_DIR, "demo_documents")
        self.documents: Dict[str, Dict[str, Any]] = {}
        self._load_documents()

    def _load_documents(self):
        if not os.path.exists(self.documents_dir):
            return

        for filename in sorted(os.listdir(self.documents_dir)):
            if filename.endswith(".json"):
                filepath = os.path.join(self.documents_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        doc_id = data.get("document_id")
                        if doc_id:
                            self.documents[doc_id] = data
                except Exception as e:
                    print(f"Error loading document {filename}: {e}")

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self.documents.get(document_id)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return list(self.documents.values())

    def retrieve(self, query: str, top_k: int = 3, target_doc_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Lexical & keyword retrieval scoring across sections of all loaded documents.
        """
        query_words = set(re.findall(r"\w+", query.lower()))
        results = []

        target_docs = self.documents.values()
        if target_doc_ids:
            target_docs = [self.documents[d] for d in target_doc_ids if d in self.documents]

        for doc in target_docs:
            doc_id = doc.get("document_id", "")
            title = doc.get("title", "")
            sections = doc.get("sections", [])

            for section in sections:
                section_id = section.get("section_id", "")
                heading = section.get("heading", "")
                content = section.get("content", "")

                text_to_match = f"{title} {heading} {content}".lower()
                text_words = set(re.findall(r"\w+", text_to_match))

                overlap = len(query_words.intersection(text_words))
                if overlap > 0 or not query_words:
                    score = overlap / max(len(query_words), 1)
                    results.append({
                        "document_id": doc_id,
                        "title": title,
                        "section_id": section_id,
                        "heading": heading,
                        "content": content,
                        "score": round(score, 3)
                    })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


# Singleton instance
_document_store = None


def get_document_store() -> DocumentStore:
    global _document_store
    if _document_store is None:
        _document_store = DocumentStore()
    return _document_store
