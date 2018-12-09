import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from async_job.models import AsyncJob
from base.models import BaseModel
from genobase.tools.s3_client import S3Client


class GeneParser(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True, primary_key=True)
    source_put_url = models.CharField(max_length=500, db_index=False, blank=True, null=True, default=None)
    is_file_uploaded = models.BooleanField(null=False, blank=False, default=False)
    is_file_processed = models.BooleanField(null=False, blank=False, default=False)
    async_job = models.ForeignKey(AsyncJob, related_name='gene_parsers', on_delete=models.CASCADE, null=True, default=None)
    file_name = models.CharField(max_length=50, db_index=False, blank=False, null=False)


@receiver(post_save, sender=GeneParser)
def gene_parser__pre_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.source_put_url = S3Client().get_presigned_put_object(
            bucket_name=S3Client.in_bucket_name,
            object_name=str(instance.id),
        )
