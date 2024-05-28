from fastapi import APIRouter

from config import s3, s3_client
import botocore
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.templating import Jinja2Templates
from services import open_file


video_router = APIRouter()

@video_router.get("/ping/video/{video_pk}")
async def ping_video(video_pk: str):
    res = False
    try:
        file_obj = s3.Object('videos', video_pk).load()
        res = True
    except botocore.exceptions.ClientError as e:
        res = False
    print(res)
    data = {'is_exist': res}
    return data

@video_router.get("/video/video/{video_pk}")
async def get_streaming_video(request: Request, video_pk: str) -> StreamingResponse:
    file, status_code, content_length, headers = await open_file(request, video_pk)
    response = StreamingResponse(
        content=file.iter_chunks(),
        media_type='video/mp4',
        status_code=status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers,
    })
    return response