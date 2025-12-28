from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
import requests

from .serializers import DocumentIngestSerializer

import logging
from datetime import date

from .utils import *

STORAGE_URL = "http://3.237.98.162:8080/documents"


def filter_and_forward(doc: dict) -> dict:
    document_id = doc.get("document_id", "UNKNOWN")

    # 1️⃣ DELETED
    if doc.get("status") == "DELETED":
        logging.info("DOC %s dropped: status=DELETED", document_id)
        return {"accepted": True, "forwarded": False, "reason": "status=DELETED"}

    # 2️⃣ empty contents
    if is_blank(doc.get("contents")):
        logging.info("DOC %s dropped: empty contents", document_id)
        return {"accepted": True, "forwarded": False, "reason": "empty contents"}

    # 3️⃣ ignore tag
    if has_ignore_tag(doc.get("tags")):
        logging.info("DOC %s dropped: ignore tag", document_id)
        return {"accepted": True, "forwarded": False, "reason": "ignore tag present"}

    # 4️⃣ valid_until → ARCHIVED (не блокирует отправку)
    try:
        vu_str = doc.get("valid_until")
        if isinstance(vu_str, str) and vu_str.strip():
            vu = parse_date_ddmmyyyy(vu_str.strip())
            if vu < date.today():
                doc["status"] = "ARCHIVED"
    except Exception:
        pass  # по ТЗ ошибок не возвращаем

    payload = to_storage_format(doc)

    # 5️⃣ Отправка в storage
    try:
        resp = requests.post(STORAGE_URL, json=[payload], timeout=10)
        if resp.status_code >= 400:
            logging.error("Storage error %s: %s", resp.status_code, resp.text)
            return {"accepted": True, "forwarded": False, "reason": f"storage error {resp.status_code}"}
    except Exception as e:
        logging.error("Storage unreachable: %s", str(e))
        return {"accepted": True, "forwarded": False, "reason": f"storage unreachable: {str(e)}"}

    # Успешная отправка
    return {"accepted": True, "forwarded": True, "reason": "success"}


class DataIngestionView(APIView):
    def post(self, request):
        serializer = DocumentIngestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"accepted": False, "reason": "invalid body"},
                status=status.HTTP_200_OK
            )

        payload = serializer.data
        payload["data_ingestion_datetime"] = now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        result = filter_and_forward(payload)
        return Response(result, status=status.HTTP_200_OK)