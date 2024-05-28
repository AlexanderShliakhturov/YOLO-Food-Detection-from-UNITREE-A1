from pydantic import BaseModel
from fastapi import Form

from fastapi.openapi.models import SecurityBase as SecurityBaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserRegister(BaseModel):
    username: str
    password: str
    confirm_password: str

class UR:
     def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
        confirm_password: str = Form(),
    ):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password


class UserInDB(User):
    hashed_password: str



class AuthForm(BaseModel):
        username: str
        password: str
     #   model: SecurityBaseModel
    # username: str
    # password: str
    # # full_name: str | None = None
    # # password: str

