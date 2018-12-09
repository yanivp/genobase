from async_job.models import AsyncJob
from base.serializers import BaseSerializer


class AsyncJobSerializer(BaseSerializer):
    class Meta:
        model = AsyncJob
        exclude = []

    def get_url(self, instance):
        return '/async_job/{id}/'.format(
            id=instance.id
        )
