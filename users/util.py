import datetime
import json
import re
from typing import List
import pandas as pd

from users.models import DocModel, RedisUserModel, User
from django.core.files.uploadedfile import InMemoryUploadedFile



class UserValidator():
    """_summary_
        a validator class for the RedisUserMOdel
    """
    def __init__(self, redis_user_obj: RedisUserModel) -> None:
        """_summary_
            Initiating the validator with a RedisUserModel Instance
        Args:
            redis_user_obj (RedisUserModel): _description_
        """
        self.user = redis_user_obj
        self.error_messages = []
        self.valid = True

    def flag_invalid(self):
        """_summary_
            Flags the validator instance as invalid
        """
        self.valid = False

    def validate_national_id(self) -> bool:
        """_summary_
            method to validate the national id
        Returns:
            bool: _description_
        """

        pattern = re.compile("[1-9]{1}[0-9]{4}[7,8]{1}[0-9]{10}")
        if re.fullmatch(pattern, self.user.national_id):
            age = datetime.date.today().year - int(self.user.national_id[1:5])
            if age >= 16:
                return True
            self.error_messages.append(
                {"national_id": "Invalid ID number! age should be greater or equal to 16"})
            self.flag_invalid()
            return False
        self.error_messages.append({"national_id": "Invalid ID number!"})
        self.flag_invalid()
        return False

    def validate_names(self) -> bool:
        """_summary_
            method to validates names
        Returns:
            bool: _description_
        """
        self.user.names = self.user.names.strip()
        if len(self.user.names) > 3:
            return True
        self.error_messages.append(
            {"names": "Should be more than 3 characters"})
        self.flag_invalid()
        return False

    def validate_gender(self) -> bool:
        """_summary_
            a method to validate gender
        Returns:
            bool: _description_
        """
        allowed_values = ["Male", "Female", "M", "F"]
        if self.user.gender in allowed_values:
            return True
        self.error_messages.append(
            {"gender": f"Invalid! allowed values are [{','.join(allowed_values)}]"})
        self.flag_invalid()
        return False

    def validate_email(self) -> bool:
        """_summary_
            a method to validate email
        Returns:
            bool: _description_
        """
        pattern = re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
        self.user.email = self.user.email.strip()
        if re.fullmatch(pattern, self.user.email):
            return True
        self.error_messages.append({"email": "Invalid Email!"})
        self.flag_invalid()
        return False

    def validate_phone_number(self) -> bool:
        """_summary_
            a method to validate phone_number
        Returns:
            bool: _description_
        """
        # see https://regex101.com/r/DsaRfI/1
        pattern = re.compile(
            "/^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$/gm")
        self.user.phone_number = f"+{self.user.phone_number.strip()}"
        if re.fullmatch(pattern, self.user.phone_number):
            return True
        self.error_messages.append({"phone_number": "Invalid phone number!"})
        self.flag_invalid()
        return False

    def validate(self) -> bool:
        """_summary_
            a method to validate a RedisUserModel instance 
        Returns:
            bool: Indicates if the instance is valid
        """
        self.validate_national_id()
        self.validate_names()
        self.validate_gender()
        self.validate_email()
        self.validate_phone_number()
        return self.valid


def validate_and_cache(file: InMemoryUploadedFile, doc_id: str):
    """_summary_
        a method to validate and cache to Redis the content of the file
    Args:
        file (InMemoryUploadedFile): uploaded file
        doc_id (str): document id assigned to the file
    """
    data = pd.read_excel(file.read())
    doc = DocModel(
        doc_id=doc_id,
        total_records=len(data),
        status="InProgress"
    )
    doc.save()
    try:
        for index, row in data.iterrows():

            # Create HashModel for Redis cache and save
            user = RedisUserModel(
                names=row['names'],
                national_id=row['NID'],
                gender=row['gender'],
                phone_number=row['phone_number'],
                email=row['email'],
                valid="True",
                doc_id=doc_id,
                processed="True",
                errors=""
            )

            validator = UserValidator(user)
            if not validator.validate():
                user.valid = "False"
                user.errors = json.dumps(validator.error_messages)
                doc.has_errors = "True"
            user.save()
            doc.processed_records += 1
            doc.save()

        doc.status = "Completed"
        doc.save()
    except Exception:
        doc.status = "Failed"
        doc.save()


def convert_and_save(users: List[RedisUserModel]):
    """_summary_
        a method convert RedisUserModels to Django User 
        instances and commit them to the database.
    Args:
        users (List[RedisUserModel]): _description_
    """
    
    user_list = []
    for user in users:
        u = User()
        u.names = user.names
        u.national_id = user.national_id
        u.phone_number = user.phone_number
        u.gender = user.gender
        u.email = user.email
        u.username = user.email

        user_list.append(u)
    User.objects.bulk_create(user_list)
