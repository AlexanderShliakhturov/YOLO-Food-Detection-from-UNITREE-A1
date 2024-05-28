from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, BackgroundTasks, UploadFile,  File
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import TokenData, User
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from db import db
import ormar
import models
from uuid import uuid4
from config import bag_bucket,producer, topic

class UserObject:
    is_authenticated: bool
    username: str | None

    def __init__(self, is_authenticated, username=None):
        self.username = username
        self.is_authenticated = is_authenticated


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return models.User.objects.get(username=username)

async def authenticate_user(db, username: str, password: str):
    user = None
    usr_obj = UserObject(False)
    try:
        user = await models.User.objects.get(username=username)
        user = user.dict()
        usr_obj.username = user['username']
        usr_obj.is_authenticated = True

    except ormar.exceptions.NoMatch:
        pass
    if not user:
        usr_obj.is_authenticated = False
    elif not verify_password(password, user.get('hashed_password')):
        usr_obj.is_authenticated = False
        usr_obj.username = None
    return usr_obj


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authorize_by_token(token: str):
    usr_obj = UserObject(False)
    if token is None:
        return usr_obj
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username is None:
            usr_obj.is_authenticated = True
            usr_obj.username = username
    except JWTError:
        pass
    if usr_obj.is_authenticated:
        user = get_user(db, username=usr_obj.username)
        if user is None:
            usr_obj.username = None
            usr_obj.is_authenticated = False
    return usr_obj


def get_current_user(token: str = Depends(oauth2_scheme)):
    print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def SendVideo(request_id, current_user: User = Depends(get_current_user), file: UploadFile = File(...), ):
    # context = {'request_id': str(uuid4())}
    # request_id = context['request_id']
    bag_bucket.put_object(Key=f'{request_id}.bag', Body=file.file)
    data = {
        'data': {
            'request_id': request_id
        }
    }

    producer.send(topic, data)
    producer.flush()
    # return context
