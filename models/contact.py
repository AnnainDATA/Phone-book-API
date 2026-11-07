from dataclasses import dataclass
from faker import Faker

fake = Faker()

@dataclass
class Contact:
    name: str
    lastName: str
    email: str
    phone: str
    address: str
    description: str

