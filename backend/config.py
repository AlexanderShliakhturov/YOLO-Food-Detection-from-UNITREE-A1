import boto3
import json
from time import sleep
import uuid
from kafka import KafkaProducer
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


s3 = boto3.resource('s3',
                        aws_access_key_id='newAccessKey',
                        aws_secret_access_key='newSecretKey',
                        endpoint_url='http://127.0.0.1:8070')

s3_client = boto3.client('s3',
                        aws_access_key_id='newAccessKey',
                        aws_secret_access_key='newSecretKey',
                        endpoint_url='http://127.0.0.1:8070')

buckets = [bucket.name for bucket in s3.buckets.all()]

if not ('bags' in buckets):
    s3.create_bucket(Bucket='bags')
bag_bucket = s3.Bucket('bags')

kafka_server = ["127.0.0.1"]

topic = "ml"

producer = KafkaProducer(
    bootstrap_servers=kafka_server,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

