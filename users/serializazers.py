from rest_framework import serializers
from users.models import User

class UserUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['names', 'national_id', 'phone_number', 'gender', 'email']
