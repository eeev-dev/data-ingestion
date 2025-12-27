from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
import requests

from .serializers import DocumentIngestSerializer

DATA_FILTRATION_SERVICE_URL = "http://13.62.126.35:8000/filter"

class DataIngestionView(APIView):
    def post(self, request):
        serializer = DocumentIngestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # данные, уже готовые для JSON
        payload = serializer.data

        # добавляем дату и время ingestion
        payload["data_ingestion_datetime"] = now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        try:
            response = requests.post(
                DATA_FILTRATION_SERVICE_URL,
                json=payload,
                timeout=5
            )
        except requests.RequestException:
            return Response(
                {"error": "Failed to forward data to filtration service"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {"status": "accepted"},
            status=status.HTTP_200_OK
        )
