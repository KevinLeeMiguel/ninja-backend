from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

from users.serializazers import UserUploadSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
import pandas as pd
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class UserView(APIView):

    parser_classes = [MultiPartParser]
    serializer_class = UserUploadSerializer

    def post(self, request):
        serialized_data = self.serializer_class(data=request.data)

        if serialized_data.is_valid():
            file: InMemoryUploadedFile = serialized_data.validated_data.get(
                "file")
            data = pd.read_excel(file.read())
            return Response(data=f"uploaded data {len(data)}", status=status.HTTP_201_CREATED)
        return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)
