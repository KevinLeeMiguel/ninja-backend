import threading
from uuid import uuid4
from rest_framework.viewsets import ViewSet
from rest_framework.parsers import MultiPartParser
from users.models import DocModel, RedisUserModel

from users.serializazers import DocSerializer, RedisUserSerializer, UserUploadSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
import pandas as pd
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from users.util import validate_and_cache


# Create your views here.
class UserViewSet(ViewSet):

    parser_classes = [MultiPartParser]
    serializer_class = UserUploadSerializer

    def create(self, request) -> Response:
        serialized_data = self.serializer_class(data=request.data)

        if serialized_data.is_valid():
            file: InMemoryUploadedFile = serialized_data.validated_data.get(
                "file")
            data = pd.read_excel(file.read())
            doc_id = uuid4().hex
            x = threading.Thread(
                target=validate_and_cache, args=(data, doc_id))
            x.start()
            return Response(data={"doc_id": doc_id}, status=status.HTTP_201_CREATED)
        return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_doc_data(self, request, pk) -> Response:
        users = RedisUserModel.find(RedisUserModel.doc_id == pk).all()
        doc = DocModel.find(DocModel.doc_id == pk).all()
        if len(doc) > 0:
            res = {
                "doc": DocSerializer(doc[0]).data,
                "data": RedisUserSerializer(users, many=True).data
            }
            return Response(data=res, status=status.HTTP_200_OK)
        return Response(data="Doc Not found!", status=status.HTTP_400_BAD_REQUEST)
