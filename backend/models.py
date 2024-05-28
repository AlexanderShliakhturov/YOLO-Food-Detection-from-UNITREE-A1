import ormar
from db import MainMeta


class User(ormar.Model):
    class Meta(MainMeta):
        pass

    hashed_password: str = ormar.String(max_length=300)
    username: str = ormar.String(max_length=100, primary_key=True)
