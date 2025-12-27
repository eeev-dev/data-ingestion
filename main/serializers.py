from rest_framework import serializers
from datetime import datetime

class SettingsSerializer(serializers.Serializer):
    visibility = serializers.ChoiceField(
        choices=["PRIVATE", "INTERNAL", "ANYONE_WITH_LINK", "PUBLIC"]
    )
    auto_save_enabled = serializers.BooleanField()


class DocumentIngestSerializer(serializers.Serializer):
    document_id = serializers.CharField()
    type = serializers.ChoiceField(
        choices=["DOCUMENT", "SPREADSHEET", "PRESENTATION", "FORM"]
    )
    status = serializers.ChoiceField(
        choices=["DRAFT", "PUBLISHED", "ARCHIVED", "DELETED"]
    )
    valid_from = serializers.DateField(
        required=False,
        input_formats=["%d-%m-%Y"]
    )
    valid_until = serializers.DateField(
        required=False,
        input_formats=["%d-%m-%Y"]
    )
    company = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    settings = SettingsSerializer()
    tags = serializers.ListField(
        child=serializers.RegexField(
            regex=r"^\S+$",
            error_messages={"invalid": "Tags must not contain spaces"}
        )
    )
    contents = serializers.CharField()

    def validate(self, data):
        valid_from = data.get("valid_from")
        valid_until = data.get("valid_until")

        if valid_from and valid_until:
            if valid_until <= valid_from:
                raise serializers.ValidationError(
                    "valid_until must be greater than valid_from"
                )

        return data
    