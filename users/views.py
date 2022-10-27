from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser

# Create your views here.
class UserView(APIView):
    
    parser_classes = [FileUploadParser]

    def post(self, request):
       data: dict = request.data['files']
       
       if 'users' in data:
           ...
