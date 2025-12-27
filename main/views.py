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

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # добавляем дату и время ingestion
        validated_data["data_ingestion_datetime"] = now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        # отправляем дальше в Data Filtration service
        try:
            response = requests.post(
                DATA_FILTRATION_SERVICE_URL,
                json=validated_data,
                timeout=5
            )
        except requests.RequestException as e:
            return Response(
                {"error": "Failed to forward data to filtration service"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {"status": "accepted"},
            status=status.HTTP_200_OK
        )
