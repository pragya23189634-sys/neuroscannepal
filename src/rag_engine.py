"""LangChain + FAISS + HuggingFace local LLM for NeuroScan Nepal RAG."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from logging_config import get_logger

logger = get_logger("rag_engine")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INDEX_DIR = DATA_DIR / "faiss_index"
KB_PATH = DATA_DIR / "medical_kb.json"

_vectorstore = None
_llm = None
_RAG_AVAILABLE: Optional[bool] = None


def rag_stack_available() -> bool:
    global _RAG_AVAILABLE
    if _RAG_AVAILABLE is not None:
        return _RAG_AVAILABLE
    try:
        import langchain_community  # noqa: F401
        import faiss  # noqa: F401
        _RAG_AVAILABLE = True
    except ImportError:
        _RAG_AVAILABLE = False
    return _RAG_AVAILABLE


def _get_embeddings():
    from langchain_community.embeddings import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def _documents_from_kb() -> list:
    from langchain_core.documents import Document

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
    return documents


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    from langchain_community.vectorstores import FAISS

    embeddings = _get_embeddings()
    if INDEX_DIR.exists() and (INDEX_DIR / "index.faiss").exists():
        logger.info("Loading FAISS index from %s", INDEX_DIR)
        _vectorstore = FAISS.load_local(
            str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
        )
    else:
        logger.info("Building FAISS index in-memory (run scripts/build_rag_index.py to persist)")
        _vectorstore = FAISS.from_documents(_documents_from_kb(), embeddings)
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        _vectorstore.save_local(str(INDEX_DIR))
    return _vectorstore


def _get_llm():
    global _llm
    if _llm is not None:
        return _llm

    try:
        from langchain_community.llms import HuggingFacePipeline
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

        logger.info("Loading local HuggingFace LLM (google/flan-t5-small) for RAG generation")
        model_name = "google/flan-t5-small"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        gen = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            max_length=160,
            truncation=True,
        )
        _llm = HuggingFacePipeline(pipeline=gen)
    except Exception as exc:
        logger.warning("Local LLM unavailable, using retrieval-only synthesis: %s", exc)
        _llm = None
    return _llm


def _retrieve(query: str, k: int = 3) -> List[Any]:
    store = _get_vectorstore()
    return store.similarity_search(query, k=k)


def _synthesize(summary_prompt: str, context: str) -> str:
    llm = _get_llm()
    if llm:
        try:
            combined = f"{summary_prompt}\n\nContext:\n{context[:900]}"
            raw = llm.invoke(combined)
            if isinstance(raw, dict):
                raw = raw.get("summary_text") or raw.get("generated_text") or str(raw)
            return str(raw)[:600].strip()
        except Exception as exc:
            logger.warning("LLM generation failed: %s", exc)
    parts = [line.strip() for line in context.split("\n") if line.strip().startswith("Content:")]
    return " ".join(p.replace("Content:", "").strip() for p in parts[:2]) or context[:400]


def generate_rag_advisory(label: str, confidence: float, top_k: int = 3) -> Dict[str, Any]:
    """LangChain FAISS retrieval + local LLM summary for pipeline advisory stage."""
    if not rag_stack_available():
        raise RuntimeError("LangChain/FAISS stack not installed")

    query = (
        f"brain MRI {label} abnormality screening medical advice neurology referral nepal"
        if label == "abnormal"
        else f"normal brain MRI routine follow-up screening nepal"
    )
    hits = _retrieve(query, k=top_k)
    snippets = [
        {
            "title": doc.metadata.get("title", ""),
            "topic": doc.metadata.get("topic", ""),
            "content": doc.page_content.split("Content:")[-1].strip() if "Content:" in doc.page_content else doc.page_content[:240],
        }
        for doc in hits
    ]
    context = "\n\n".join(doc.page_content for doc in hits)
    sources = sorted({doc.metadata.get("source", doc.metadata.get("title", "Medical KB")) for doc in hits})

    prompt = (
        f"Write two sentences of clinician-facing guidance for a {label} brain MRI screening result."
    )
    summary = _synthesize(prompt, context)

    return {
        "summary": summary,
        "snippets": snippets,
        "sources": sources,
        "confidence_note": f"Model confidence: {confidence:.1%}",
        "disclaimer": "Prototype RAG output (LangChain + FAISS + local LLM). Not medical advice.",
        "retrieval_mode": "langchain_faiss_llm",
        "documents_matched": len(hits),
        "document_count": len(_documents_from_kb()),
    }


def generate_chat_answer(message: str, label: str, language: str = "en") -> Dict[str, str]:
    """Context-aware bilingual answer using FAISS retrieval + FAQ fallback + LLM."""
    faq_path = DATA_DIR / "chatbot_faq.json"
    faq = json.loads(faq_path.read_text(encoding="utf-8")) if faq_path.exists() else []
    tokens = set(re.findall(r"[a-z0-9]+", message.lower()))
    best_score = -1.0
    best_entry = None
    for entry in faq:
        keywords = set(re.findall(r"[a-z0-9]+", " ".join(entry.get("keywords", [])).lower()))
        score = len(tokens & keywords) * 2
        if label in entry.get("labels", []):
            score += 2
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score > 0:
        answer = best_entry.get("answer_ne" if language == "ne" else "answer_en", "")
        return {
            "answer": answer,
            "matched_faq": best_entry.get("id", ""),
            "language": language,
            "mode": "faq_bilingual",
        }

    if rag_stack_available():
        query = f"{message} brain MRI {label} nepal patient advice"
        hits = _retrieve(query, k=2)
        context = "\n".join(doc.page_content for doc in hits)
        if language == "ne":
            prompt = f"Answer in simple Nepali for patient question about {label} MRI: {message}"
        else:
            prompt = f"Answer the patient question about a {label} brain MRI scan: {message}"
        answer = _synthesize(prompt, context)
        return {
            "answer": answer,
            "matched_faq": "",
            "language": language,
            "mode": "langchain_faiss_llm",
        }

    fallback_en = "Please consult a qualified clinician for personalised advice about this scan."
    fallback_ne = "यो scan बारे personalised advice का लागि qualified clinician सँग consult गर्नुहोस्।"
    return {
        "answer": fallback_ne if language == "ne" else fallback_en,
        "matched_faq": "",
        "language": language,
        "mode": "fallback",
    }
