# from __future__ import absolute_import
# from celery import Celery
# from django.conf import settings
#
# app = Celery(
#     'genobase',
#     # broker='amqp://admin:mypass@{}:5672'.format(
#     #     'rabbit'  # if settings.IS_DOCKER else 'localhost'
#     # ),
#     broker='redis://redis:6379/0',
#     backend='rpc://',
#     include=[
#         'gene_parser.tasks'
#     ],
#     task_always_eager=True,
# )


import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genobase.settings')

app = Celery('genobase')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
