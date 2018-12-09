from rest_framework import serializers
from base.serializers import BaseSerializer
from gene.models import Gene
from gene_parser.serializers import GeneParserSerializer


class GeneSerializer(BaseSerializer):
    id = serializers.ReadOnlyField()
    gene_parser = GeneParserSerializer(read_only=True)

    class Meta:
        model = Gene
        exclude = ['is_file_uploaded']

    def get_url(self, instance):
        return '/gene/{id}/'.format(
            id=instance.id
        )
