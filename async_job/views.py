from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from async_job.models import AsyncJob
from async_job.serializers import AsyncJobSerializer


class AsyncJobViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    serializer_class = AsyncJobSerializer
    queryset = AsyncJob.objects.all()
