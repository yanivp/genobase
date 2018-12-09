from rest_framework import serializers
from async_job.serializers import AsyncJobSerializer
from base.serializers import BaseSerializer
from gene_parser import parsers
from gene_parser.models import GeneParser
from genobase.tools.s3_client import S3Client


class GeneParserSerializer(BaseSerializer):
    class Meta:
        model = GeneParser
        exclude = [
            'is_file_uploaded',
        ]

    id = serializers.ReadOnlyField()
    source_put_url = serializers.ReadOnlyField()
    is_file_processed = serializers.ReadOnlyField()
    async_job = async_job = AsyncJobSerializer(read_only=True)
    file_name = serializers.RegexField(
        regex="^.*\\.({})$".format(
            '|'.join(parsers.supported_file_types)
        )
    )
    processed_file_url = serializers.SerializerMethodField()

    def get_processed_file_url(self, instance):
        if not instance.is_file_processed:
            return None

        return S3Client().get_presigned_get_object(
            bucket_name=S3Client.out_bucket_name,
            object_name=str(instance.id)
        )

    def get_url(self, instance):
        return '/gene_parser/{id}/'.format(
            id=instance.id
        )
