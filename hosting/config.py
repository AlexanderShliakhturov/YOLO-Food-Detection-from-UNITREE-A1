import boto3
from time import sleep

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
videos_bucket = s3.Bucket('videos')
