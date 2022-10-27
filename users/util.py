import pandas as pd

from users.models import RedisUserModel

def validate_and_cache(data: pd.DataFrame, doc_id: str):
    
    for index, row in data.iterrows():
        
        # Create HashModel for Redis cache and save
        user = RedisUserModel(
            names=row['names'],
            national_id=row['NID'],
            gender=row['gender'],
            phone_number=row['phone_number'],
            email=row['email'],
            valid="True",
            doc_id=doc_id
        )
    
        user.save()
        
    