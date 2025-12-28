from datetime import datetime, date
from typing import Any, Dict, List

def parse_date_ddmmyyyy(s: str) -> date:
    return datetime.strptime(s, "%d-%m-%Y").date()


def is_blank(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


def has_ignore_tag(tags: Any) -> bool:
    if not isinstance(tags, list):
        return False
    return any(isinstance(t, str) and t.strip().lower() == "ignore" for t in tags)


def to_storage_format(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc_copy = doc.copy()
    doc_copy.pop("document_id", None)

    return {
        "document_id": doc.get("document_id"),
        "document_data": doc_copy,
    }
