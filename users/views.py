import threading
from uuid import uuid4
from rest_framework.viewsets import ViewSet
from rest_framework.parsers import MultiPartParser
from users.models import DocModel, RedisUserModel

from users.serializazers import DocSerializer, RedisUserSerializer, UserUploadSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction


from users.util import convert_and_save, validate_and_cache


# Create your views here.
class UserViewSet(ViewSet):
    """_summary_
    a set of views to handle file upload, cache, 
    validaation, progress status, and commit
    Args:
        ViewSet (_type_): _description_

    Returns:
        _type_: _description_
    """

    parser_classes = [MultiPartParser]
    serializer_class = UserUploadSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request) -> Response:
        """_summary_
        a view method to handle file upload and cache to Redis 
        Args:
            request (_type_): _description_

        Returns:
            Response: _description_
        """
        serialized_data = self.serializer_class(data=request.data)

        if serialized_data.is_valid():
            file: InMemoryUploadedFile = serialized_data.validated_data.get(
                "file")
            doc_id = uuid4().hex

            # Initiate a thread that will handle the validation and caching of the uploaded file
            x = threading.Thread(
                target=validate_and_cache, args=(file, doc_id))
            # start the validation and caching thread
            x.start()
            return Response(data={"doc_id": doc_id}, status=status.HTTP_201_CREATED)
        return Response(data=serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_doc_data(self, request, pk) -> Response:
        """_summary_
            a method to retrieve the uploaded file status 
            and the uploaded data with validation errors if any
        Args:
            request (_type_): django request object
            pk (_type_): the document id returned after the upload was successful

        Returns:
            Response: _description_
        """
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
    @transaction.atomic
    def commit(self, request, pk) -> Response:
        """_summary_
            a method to commit valid entries from the uploaded file
        Args:
            request (_type_): django request object
            pk (_type_): the document id returned after the upload was successful

        Returns:
            Response: _description_
        """
        doc = DocModel.find(DocModel.doc_id == pk).all()
        if len(doc) > 0:
            if doc[0].status != "Completed":
                error_message = "Doc validation still in progress" if doc[0].status == "InProgress" else "Doc validation failed! try uploading a new file"
                return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)
            users = RedisUserModel.find((RedisUserModel.doc_id == pk) & (RedisUserModel.valid == "True")).all()
            # determine the number of batches we need in order to bulksave 2000 entries at a time
            j = int(len(users)/2000)
            batches = j if j%2000 == 0 else j+1
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
        