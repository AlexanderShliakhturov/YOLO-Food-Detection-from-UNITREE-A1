from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
import shutil
from typing import List
from uuid import uuid4
from schemas import UploadVideo, GetVideo, User
from models import Video, User
from typing import IO, Generator
from pathlib import Path
from starlette.requests import Request
from starlette.responses import StreamingResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from services import write_video, open_file





video_router = APIRouter()
templates = Jinja2Templates(directory='templates')



@video_router.post("/")
async def create_video(
    background_tasks: BackgroundTasks,
    #title: str = Form(...),
    #description: str = Form(...),
    file: UploadFile = File(...),
):  
    user = User(18, username='nikita')
    #user=await User.objects.first()
    file_name = f'media/{uuid4()}.mp4'
    if file.content_type =='video/mp4':
        background_tasks.add_task(write_video, file_name, file)
        #await write_video(file_name, file)
    else:
        raise HTTPException(status_code=418, detail='It is not mp4')
    return await Video.objects.create(file=file_name, user=user)



@video_router.get("/index/{video_pk}", response_class=HTMLResponse)
async def get_video(request: Request, video_pk: int):
    return templates.TemplateResponse("index.html", {"request": request, "path": video_pk})


@video_router.get("/video/video/{video_pk}")
async def get_streaming_video(request: Request, video_pk: int) -> StreamingResponse:
    file, status_code, content_length, headers = await open_file(request, video_pk)
    response = StreamingResponse(
        file,
        media_type='video/mp4',
        status_code=status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers,
    })
    return response




@video_router.get("/video/{video_pk}")
async def get_video(video_pk: int):
    file = await Video.objects.select_related('user').get(pk=video_pk)
    file_like = open(file.dict().get('file'),mode = 'rb')
    return StreamingResponse(file_like, media_type='video/mp4')

