import json
import logging
from celery import signals, states
from django.conf import settings
from django.db import transaction
from async_job.models import AsyncJob

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def set_async_job_state(async_job_id, state):
    with transaction.atomic():
        try:
            async_job = AsyncJob.objects.get(pk=async_job_id)
            async_job.state = state
            async_job.save()
        except AsyncJob.DoesNotExist:
            logger.error('Could not retrieve AsyncJob {}'.format(str(async_job_id)))
        else:
            logger.info('Task state set to {}'.format(state))


@signals.task_prerun.connect
def pre_task(task_id=None, task=None, *args, **kwargs):
    async_job_json = json.loads(kwargs['kwargs']['async_job_json_string'])
    logger.error('AsyncJob {} started'.format(str(async_job_json['pk'])))
    set_async_job_state(async_job_json['pk'], AsyncJob.State.Started['id'])


celery_states = {
    states.PENDING: AsyncJob.State.Pending,
    states.STARTED: AsyncJob.State.Started,
    states.SUCCESS: AsyncJob.State.Success,
    states.FAILURE: AsyncJob.State.Failure,
    states.RETRY: AsyncJob.State.Retry,
    states.REVOKED: AsyncJob.State.Revoked,
}


@signals.task_postrun.connect
def post_task(task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    async_job_json = json.loads(kwargs['kwargs']['async_job_json_string'])
    logger.info('JSON: ' + str(async_job_json))
    logger.error(
        'AsyncJob {} {}'.format(
            str(async_job_json['pk']),
            celery_states[state]['value']
        )
    )
    set_async_job_state(async_job_json['pk'], celery_states[state]['id'])
