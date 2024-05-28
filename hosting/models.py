from ormar import Model
import ormar
from db import metadata, database
import datetime
from typing import Optional


class MainMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(Model):
    class Meta(MainMeta):
        pass
    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=100)

class Video(Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    file:str = ormar.String(max_length=1000)
    create_at: datetime.datetime = ormar.DateTime(default = datetime.datetime.now)
    user: Optional[User] = ormar.ForeignKey(User)