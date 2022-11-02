import email
from django.test import TestCase
import requests

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import User


class AccountTests(APITestCase):
    def __init__(self, methodName: str = ...) -> None:
        # SetUp User
        # self.user = self.setup_user()
        self.doc_id = ""
        self.client = APIClient()
        super().__init__(methodName)

    def setup_user(self):
        User.objects.filter(email="test-user@yopmail.com").delete()
        user = User()
        user.names = "Test User"
        user.national_id = "1199680123456852"
        user.phone_number = "+250789270784"
        user.gender = "M"
        user.email = "test-user@yopmail.com"
        user.username = "test-user@yopmail.com"
        user.is_active = True
        user.set_password("test123")
        user.save()
        self.user = user

    def get_token(self):
        self.setup_user()
        payload = {
            'email': self.user.email,
            'password': "test123"
        }
        response = self.client.post('/api/token/', data=payload)

        return response.data.get('access')

    def test_sign_in(self):
        self.setup_user()
        """
        ensure a user can signin and receive an jwt token
        """
        payload = {
            'email': "test-user@yopmail.com",
            'password': "test123"
        }
        response = self.client.post('/api/token/', data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_upload_users_file(self):
        """
        Ensure we can upload users file.
        """
        client = APIClient()
        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.get_token()}")
        response = client.post('/api/users/', {
            "file": open("users/tests/test_data/test_users.xlsx", "rb"),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('doc_id' in response.data)
