import logging
import uuid
from django.conf import settings
from django.db import models, transaction
from django.contrib.postgres.fields import JSONField
import json
from django.core import serializers
from base.models import BaseModel


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class AsyncJob(BaseModel):
    class State(object):
        Pending = {'id': '1', 'value': 'Pending'}
        Started = {'id': '2', 'value': 'Started'}
        Success = {'id': '3', 'value': 'Success'}
        Failure = {'id': '4', 'value': 'Failure'}
        Retry = {'id': '5', 'value': 'Retry'}
        Revoked = {'id': '6', 'value': 'Revoked'}

    STATES = (
        (State.Pending['id'], State.Pending['value']),
        (State.Started['id'], State.Started['value']),
        (State.Success['id'], State.Success['value']),
        (State.Failure['id'], State.Failure['value']),
        (State.Retry['id'], State.Retry['value']),
        (State.Revoked['id'], State.Revoked['value']),
    )

    id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True, primary_key=True)
    job_name = models.CharField(max_length=200, db_index=True)
    job_payload = JSONField(db_index=False, null=True, blank=True, default=dict)
    job_settings = JSONField(db_index=False, null=True, blank=True, default=dict)
    progress_data = JSONField(db_index=False, null=True, blank=True, default=dict)
    results = JSONField(db_index=False, null=True, blank=True, default=dict)
    state = models.CharField(max_length=1, choices=STATES, null=True, blank=True, default=State.Pending['id'], db_index=True)

    @staticmethod
    def produce_job(
        async_task_func,
        job_payload=dict(),
    ):
        with transaction.atomic():
            async_job = AsyncJob()
            async_job.name = str(async_task_func)
            async_job.job_payload = job_payload
            async_job.async_state = AsyncJob.State.Pending['id'],
            async_job.save()

            async_job_json = serializers.serialize('json', [async_job, ])
            struct = json.loads(async_job_json)
            async_job_json_string = json.dumps(struct[0])

            params = {
                'async_job_json_string': async_job_json_string
            }

            logger.info('Sending task to broker: {}'.format(async_job_json_string))
            if settings.CELERY_TASK_CALL_DIRECT:
                async_task_func(**params)
            else:
                async_task_func.apply_async(kwargs=params)

        return async_job
