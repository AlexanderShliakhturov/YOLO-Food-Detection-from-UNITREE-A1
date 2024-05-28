import boto3
import json
from time import sleep
import uuid
import os
from pipeline_pocessing import yolo_procces
from kafka import KafkaConsumer
from bag_processing import get_csv, get_depth_video, get_rgb_video, delete_videos
s3 = boto3.resource('s3',
                        aws_access_key_id='newAccessKey',
                        aws_secret_access_key='newSecretKey',
                        endpoint_url='http://127.0.0.1:8070')

s3_client = boto3.client('s3',
                        aws_access_key_id='newAccessKey',
                        aws_secret_access_key='newSecretKey',
                        endpoint_url='http://127.0.0.1:8070')

buckets = [bucket.name for bucket in s3.buckets.all()]

if not ('videos' in buckets):
    s3.create_bucket(Bucket='videos')
video_bucket = s3.Bucket('videos')

kafka_server = ["127.0.0.1"]

topic = "ml"

consumer = KafkaConsumer(
    bootstrap_servers=kafka_server,
    value_deserializer=json.loads,
    auto_offset_reset="latest",
)

consumer.subscribe(topic)

while True:
    data = next(consumer)
    print(data)
    print(data.value['data'])
    request_id = data.value['data']['request_id']

    s3_client.download_file('bags', request_id + '.bag', f'media/{request_id}.bag')
    s3.Object('bags', request_id + '.bag').delete()

    get_csv(request_id)
    get_depth_video(request_id)
    get_rgb_video(request_id)
    yolo_procces(request_id)

    data = open(f'media/{request_id}-depth.mp4', 'rb')
    video_bucket.put_object(Key=f'{request_id}-depth.mp4', Body=data) # загрузка depth файла
    data.close()
    data = open(f'media/{request_id}-rgb.mp4', 'rb')
    video_bucket.put_object(Key=f'{request_id}-rgb.mp4', Body=data) # загрузка rgb файла
    data.close()
    data = open(f'media/{request_id}-pipline.mp4', 'rb')
    video_bucket.put_object(Key=f'{request_id}-pipline.mp4', Body=data) # загрузка pipline файла
    data.close()
    delete_videos(request_id)
