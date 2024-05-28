import shutil
import ormar
from pathlib import Path
from typing import IO, Generator
from uuid import uuid4
import boto3
import botocore
from fastapi import UploadFile, BackgroundTasks, HTTPException
from starlette.requests import Request
from config import s3, s3_client, buckets
from models import Video, User
from schemas import UploadVideo



def write_video(file_name:str, file: UploadFile):
    with open (file_name, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

def ranged(
        file: IO[bytes],
        start: int = 0,
        end: int = None,
        block_size: int = 8192,
) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)
    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size
        if data_length <= 0:
            break
        data = file.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(file, 'close'):
        file.close()

async def open_file(request: Request, video_pk: str) -> tuple:
    try:
        file_obj = s3_client.get_object(Bucket='videos', Key=video_pk)
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=404, detail="Not found")
    file_obj = s3_client.get_object(Bucket='videos', Key=video_pk)
    file_size = file_obj['ContentLength']
    content_length = file_size
    status_code = 200
    headers = {}
    content_range = request.headers.get('range')

    if content_range is not None:
        content_range = content_range.strip().lower()
        content_ranges = content_range.split('=')[-1]
        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
        content_length = (range_end - range_start) + 1
        file_obj = s3_client.get_object(Bucket='videos', Key=video_pk, Range=f'bytes={range_start}-{range_end}')
        status_code = 206
        headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

    return file_obj['Body'], status_code, content_length, headers