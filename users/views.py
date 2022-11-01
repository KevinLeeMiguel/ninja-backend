from symbol import star_expr
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

from users.util import convert_and_save, validate_and_cache


# Create your views here.
class UserViewSet(ViewSet):

    parser_classes = [MultiPartParser]
    serializer_class = UserUploadSerializer

    def create(self, request) -> Response:
        serialized_data = self.serializer_class(data=request.data)

        if serialized_data.is_valid():
            file: InMemoryUploadedFile = serialized_data.validated_data.get(
                "file")
            doc_id = uuid4().hex
            x = threading.Thread(
                target=validate_and_cache, args=(file, doc_id))
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

    @action(detail=True, methods=['get'])
    def commit(self, request, pk) -> Response:
        doc = DocModel.find(DocModel.doc_id == pk).all()
        if len(doc) > 0:
            if doc[0].status != "Completed":
                error_message = "Doc validation still in progress" if doc[0].status == "InProgress" else "Doc validation failed! try uploading a new file"
                return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)
            users = RedisUserModel.find((RedisUserModel.doc_id == pk) & (RedisUserModel.valid == "True")).all()
            j = int(len(users)/2000)
            batches = j if j%2000 == 0 else j+1
            print(len(users))
            for i in range(0,batches):
                if i == batches-1:
                    start = 2000*i
                    convert_and_save(users[start:])
                else:
                    start = 2000*i
                    end = (2000*i) + 2000
                    convert_and_save(users[start:end])
            
            return Response(status=status.HTTP_201_CREATED)
        return Response(data="Doc Not found!", status=status.HTTP_400_BAD_REQUEST)
        