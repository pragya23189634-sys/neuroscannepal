"""Medical knowledge base, hospital directory, and bilingual FAQ retrieval for NeuroScan Nepal."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
HOSPITALS_PATH = DATA_DIR / "hospitals_nepal.json"
HEALTHCARE_PATH = DATA_DIR / "nepal_healthcare.json"
MEDICAL_KB_PATH = DATA_DIR / "medical_kb.json"
CHATBOT_FAQ_PATH = DATA_DIR / "chatbot_faq.json"

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_hospitals() -> List[Dict[str, str]]:
    return _load_json(HOSPITALS_PATH, [])


def load_healthcare_extras() -> Dict[str, Any]:
    return _load_json(HEALTHCARE_PATH, {"government_programs": [], "cost_reference": []})


def load_medical_documents() -> List[Dict[str, Any]]:
    return _load_json(MEDICAL_KB_PATH, [])


def load_chatbot_faq() -> List[Dict[str, Any]]:
    return _load_json(CHATBOT_FAQ_PATH, [])


def get_healthcare_bundle(label: str) -> Dict[str, Any]:
    """Hospitals + government programmes + cost reference for Nepal."""
    hospitals = filter_hospitals(label)
    extras = load_healthcare_extras()
    return {
        "hospitals": hospitals,
        "government_programs": extras.get("government_programs", []),
        "cost_reference": extras.get("cost_reference", []),
        "hospital_count": len(hospitals),
        "program_count": len(extras.get("government_programs", [])),
    }


def retrieve_medical_context(label: str, confidence: float, top_k: int = 3) -> Dict[str, Any]:
    """LangChain + FAISS + local LLM when available; keyword fallback otherwise."""
    try:
        from rag_engine import generate_rag_advisory, rag_stack_available

        if rag_stack_available():
            return generate_rag_advisory(label, confidence, top_k=top_k)
    except Exception:
        pass
    return _retrieve_keyword(label, confidence, top_k)


def _retrieve_keyword(label: str, confidence: float, top_k: int) -> Dict[str, Any]:
    docs = load_medical_documents()
    query_tokens = _tokenize(f"{label} brain mri abnormality screening nepal")
    if label == "abnormal":
        query_tokens |= _tokenize("tumour tumor lesion referral neurology oncology biopsy")
    else:
        query_tokens |= _tokenize("normal routine follow-up screening negative")

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for doc in docs:
        haystack = " ".join(
            str(doc.get(key, "")) for key in ("title", "topic", "content", "keywords", "labels")
        )
        doc_tokens = _tokenize(haystack)
        if not doc_tokens:
            continue
        overlap = len(query_tokens & doc_tokens)
        label_match = 1.0 if label in doc.get("labels", []) else 0.0
        score = overlap + label_match * 2.0
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    hits = [doc for _, doc in scored[:top_k]]

    if not hits:
        fallback = (
            "No abnormality detected in this scan slice. Continue routine follow-up as advised by your clinician."
            if label == "normal"
            else "Possible abnormality detected. Recommend neurology/oncology referral for confirmatory review."
        )
        return {
            "summary": fallback,
            "snippets": [],
            "sources": ["NeuroScan prototype knowledge base"],
            "confidence_note": f"Model confidence: {confidence:.1%}",
            "disclaimer": "Prototype RAG output for research demonstration only. Not medical advice.",
            "retrieval_mode": "fallback",
            "documents_matched": 0,
            "document_count": len(docs),
        }

    summary_parts = [hit["content"] for hit in hits[:2]]
    sources = sorted({hit.get("source", hit.get("title", "Medical KB")) for hit in hits})
    return {
        "summary": " ".join(summary_parts),
        "snippets": [{"title": h.get("title"), "topic": h.get("topic"), "content": h.get("content")} for h in hits],
        "sources": sources,
        "confidence_note": f"Model confidence: {confidence:.1%}",
        "disclaimer": "Prototype RAG output for research demonstration only. Not medical advice.",
        "retrieval_mode": "keyword_retrieval",
        "documents_matched": len(hits),
        "document_count": len(docs),
    }


def initial_chatbot_message(label: str) -> Dict[str, Any]:
    if label == "abnormal":
        english = (
            "The scan may show an abnormality. Please consult a neurologist for further evaluation. "
            "You can ask about next steps, hospitals, costs, or what this result means."
        )
        nepali = (
            "स्क्यानमा असामान्यता देखिएको हुन सक्छ। थप जाँचका लागि neurologist/sँग consult गर्नुहोस्। "
            "अर्को कदम, अस्पताल, खर्च, वा नतिजाको अर्थ सोध्न सक्नुहुन्छ।"
        )
    else:
        english = (
            "No major abnormality was detected in this slice. Follow routine clinical follow-up. "
            "Ask me about follow-up, hospitals, government programmes, or screening limitations."
        )
        nepali = (
            "यो slice मा ठूलो असामान्यता देखिएन। नियमित clinical follow-up गर्नुहोस्। "
            "follow-up, अस्पताल, सरकारी programme, वा screening सीमाबारे सोध्न सक्नुहुन्छ।"
        )
    return {
        "language_en": english,
        "language_ne": nepali,
        "mode": "bilingual_langchain",
    }


def answer_chatbot(message: str, label: str, language: str = "en") -> Dict[str, str]:
    try:
        from rag_engine import generate_chat_answer

        return generate_chat_answer(message, label, language)
    except Exception:
        pass
    return _answer_faq_only(message, label, language)


def _answer_faq_only(message: str, label: str, language: str) -> Dict[str, str]:
    faq = load_chatbot_faq()
    tokens = _tokenize(message)
    if not tokens:
        tokens = _tokenize(label)

    best_score = -1.0
    best_entry: Dict[str, Any] | None = None
    for entry in faq:
        keywords = _tokenize(" ".join(entry.get("keywords", [])))
        question = _tokenize(entry.get("question_en", ""))
        score = len(tokens & keywords) * 2 + len(tokens & question)
        if label in entry.get("labels", []):
            score += 2
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score > 0:
        answer = best_entry.get("answer_ne" if language == "ne" else "answer_en", "")
        return {"answer": answer, "matched_faq": best_entry.get("id", ""), "language": language, "mode": "faq"}

    default = (
        "यो प्रणाली academic prototype हो। qualified clinician सँग consult गर्नुहोस्।"
        if language == "ne"
        else "This is an academic prototype. Please consult a qualified clinician."
    )
    return {"answer": default, "matched_faq": "", "language": language, "mode": "fallback"}


def filter_hospitals(label: str, limit: int | None = None) -> List[Dict[str, str]]:
    hospitals = load_hospitals()
    if label != "abnormal":
        hospitals = hospitals[: min(4, len(hospitals))]
    if limit:
        hospitals = hospitals[:limit]
    return hospitals
