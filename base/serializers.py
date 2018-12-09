from rest_framework import serializers
from async_job.models import AsyncJob


class BaseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        raise NotImplemented()
