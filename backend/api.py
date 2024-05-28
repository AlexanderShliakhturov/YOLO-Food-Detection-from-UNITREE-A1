import shutil
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from fastapi import Depends, HTTPException, status, Body, Cookie, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi import APIRouter, UploadFile, File
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import Token, User, UR
import models

from fastapi.templating import Jinja2Templates
from func import create_access_token, get_current_user, get_password_hash, get_user, authenticate_user, authorize_by_token, SendVideo



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/rest-register")
async def rest_register(form_data: UR = Depends()):
    context = {'is_succes': False}
    print(form_data.confirm_password == form_data.password)
    if (form_data.password == form_data.confirm_password):
        # проверка совпадений пас и конпас изернейм уникален пароль по длинне
        if (len(form_data.password) >= 10) and form_data.password != form_data.username:
            if (await models.User.objects.get_or_none(username=form_data.username) is None):
                context['is_succes'] = True
                password = get_password_hash(form_data.password)
                usr = models.User(username=form_data.username, hashed_password=password)
                await usr.save()
    return context

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data:  OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(models.User, form_data.username, form_data.password)
    if not user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_user)):
    return [{"item_id": "Foo", "owner": (await current_user).username}]

@router.get('/logout', response_class=RedirectResponse)
def logout():
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="session", value="")
    return resp

@router.get('/')
def index(session: str | None = Cookie(default=None)):
    user = authorize_by_token(session)
    if not user.is_authenticated:
        return RedirectResponse(url="/about", status_code=status.HTTP_302_FOUND) #поменять на about
    return templates.TemplateResponse("index.html", {"request": {"user": user}})

@router.post("/upload-file")
async def upload_file(back_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), file: UploadFile = File(...),):
    print(file.filename[-4:])
    if file.filename[-4:] != ".bag":
        context = {'request_id': 'not_valid'}
        return context
    context = {'request_id': str(uuid4())}
    request_id = context['request_id']
    back_tasks.add_task(SendVideo, request_id, current_user, file)
    return context
    # bag_bucket.put_object(Key=f'{request_id}.bag', Body=file.file)
    # data = {
    #     'data': {
    #         'request_id': request_id
    #     }
    # }
    # producer.send(topic, data)
    # producer.flush()
    # return context
    
    
@router.get('/login')
def login(session: str | None = Cookie(default=None)):
    user = authorize_by_token(session)
    if user.is_authenticated:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": {}})

@router.get('/register')
def register(session: str | None = Cookie(default=None)):
    user = authorize_by_token(session)
    if user.is_authenticated:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": {}})

@router.get('/about')
def about():
    return templates.TemplateResponse("about1.html", {"request": {}})