import numpy as np
import random
import string
import pandas as pd 

ids = np.random.randint(1199971111111111, 1200589999999999, 50000)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def generate_random_phone_number():
    prefixes = ['+25078', '+25079', '+25072', '+25073']
    numbers = [0,1,2,3,4,5,6,7,8,9]
    return f'{random.choice(prefixes)}{"".join(str(random.choice(numbers)) for i in range(7))}'

names = []
genders = []
phone_numbers = []
emails = []
for i in range(50000):
    names.append(f"{get_random_string(8)} {get_random_string(8)}")
    genders.append(random.choice(["M", "F", "Not Supported"]))
    phone_numbers.append(f"{generate_random_phone_number()}")
    emails.append(f"{get_random_string(12)}@yopmail.com")



df = pd.DataFrame({
    "NID": ids,
    "names": names,
    "gender": genders,
    "email": emails, 
    "phone_number": phone_numbers,
})

df.to_excel('./users.xlsx', index=False)