import imp
from rest_framework import serializers
from users.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

class UserUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    
    def validate_file(self, value: InMemoryUploadedFile) -> InMemoryUploadedFile:
        """_summary_

        Args:
            value (TemporaryUploadedFile): _description_

        Raises:
            serializers.ValidationError: _description_

        Returns:
            TemporaryUploadedFile: _description_
        """
        if value.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            return value
        raise serializers.ValidationError("Please upload an excel file!")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['names', 'national_id', 'phone_number', 'gender', 'email']
