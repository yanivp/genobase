import os
from datetime import timedelta
from minio import Minio
from minio.error import ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists

S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', '')

_minio_client = Minio(
    's3:9000',
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
    secure=False,
)


class S3Client:
    """Implements a simple S3 client using Minio"""

    in_bucket_name = os.environ['S3_IN_BUCKET_NAME']
    out_bucket_name = os.environ['S3_OUT_BUCKET_NAME']

    def __init__(self):
        # Make sure buckets exist
        self.create_bucket(S3Client.in_bucket_name)
        self.create_bucket(S3Client.out_bucket_name)

    def create_bucket(self, bucket_name, location='us-east-1'):
        """Create a bucket to work with"""
        try:
            _minio_client.make_bucket(
                bucket_name=bucket_name,
                location=location
            )
        except BucketAlreadyOwnedByYou:
            pass
        except BucketAlreadyExists:
            pass
        except ResponseError:
            raise

    def get_presigned_get_object(self, bucket_name, object_name, expires=timedelta(days=7)):
        """Get a presigned object for GET operation"""
        try:
            return _minio_client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )
        except ResponseError:
            raise

    def get_presigned_put_object(self, bucket_name, object_name, expires=timedelta(days=7)):
        """Get a presigned object for PUT operation"""
        try:
            return _minio_client.presigned_put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )
        except ResponseError:
            raise

    def get_partial_object(self, bucket_name, object_name, offset, length):
        try:
            return _minio_client.get_partial_object(
                bucket_name=bucket_name,
                object_name=object_name,
                offset=offset,
                length=length
            )
        except ResponseError:
            raise

    def stat_object(self, bucket_name, object_name):
        try:
            return _minio_client.stat_object(
                bucket_name=bucket_name,
                object_name=object_name
            )
        except ResponseError:
            raise

    def remove_object(self, bucket_name, object_name):
        try:
            return _minio_client.remove_object(
                bucket_name=bucket_name,
                object_name=object_name
            )
        except ResponseError:
            raise

    def put_object(
        self, bucket_name, object_name, data, length, content_type='application/octet-stream', metadata=None
    ):
        try:
            return _minio_client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                metadata=metadata
            )
        except ResponseError:
            raise
