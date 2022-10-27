from django.apps import apps
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from redis_om.model import HashModel


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    names = models.CharField(max_length=255)
    national_id = models.BigIntegerField()
    phone_number = models.CharField(max_length=50)
    gender = models.CharField(max_length=50, choices=[
                              ('M', 'Male'), ('F', 'Female')])
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['national_id', 'phone_number', 'gender', 'names']

    objects = CustomUserManager()


class RedisUserModel(HashModel):
    """_summary_
    This is a redis_om HashModel to help us in storing the not yet comitted uploaded users

    Args:
        HashModel (_type_): _description_
    """
    names: str
    national_id: str
    gender: str
    phone_number: str
    email: str
    valid: str
    doc_id: str
