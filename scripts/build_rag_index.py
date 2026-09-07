#!/usr/bin/env python3
"""Build LangChain FAISS vector index from medical_kb.json (53+ documents)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INDEX_DIR = DATA_DIR / "faiss_index"
KB_PATH = DATA_DIR / "medical_kb.json"


def main() -> None:
    if not KB_PATH.exists():
        raise SystemExit(f"Missing {KB_PATH}")

    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain_core.documents import Document
    except ImportError:
        raise SystemExit("Install RAG deps: pip install langchain langchain-community faiss-cpu sentence-transformers")

    docs_raw = json.loads(KB_PATH.read_text(encoding="utf-8"))
    documents = []
    for item in docs_raw:
        text = (
            f"Title: {item.get('title', '')}\n"
            f"Topic: {item.get('topic', '')}\n"
            f"Labels: {', '.join(item.get('labels', []))}\n"
            f"Keywords: {item.get('keywords', '')}\n"
            f"Content: {item.get('content', '')}"
        )
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "id": item.get("id", ""),
                    "title": item.get("title", ""),
                    "topic": item.get("topic", ""),
                    "source": item.get("source", "NeuroScan medical KB"),
                },
            )
        )

    print(f"Embedding {len(documents)} documents with sentence-transformers/all-MiniLM-L6-v2 ...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    store = FAISS.from_documents(documents, embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(INDEX_DIR))
    print(f"Saved FAISS index to {INDEX_DIR}")


if __name__ == "__main__":
    main()
