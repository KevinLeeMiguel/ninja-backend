import pandas as pd

from users.models import DocModel, RedisUserModel


def validate_and_cache(data: pd.DataFrame, doc_id: str):

    doc = DocModel(
        doc_id=doc_id,
        total_records=len(data),
        status="InProgress"
    )
    doc.save()
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
            processed="True"
        )

        user.save()
        doc.processed_records += 1
        doc.save()
    doc.status = "Completed"
    doc.save()
