from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from async_job.models import AsyncJob
from gene_parser.tasks import process_genes
from gene_parser.models import GeneParser
from gene_parser.serializers import GeneParserSerializer


class GeneParserViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin
):
    serializer_class = GeneParserSerializer
    queryset = GeneParser.objects.all()

    @action(detail=True, methods=['post'])
    def file_uploaded(self, request, *args, **kwargs):
        # Load the GeneParser
        pk = kwargs['pk']

        gene_parser = GeneParser.objects.get(pk=pk)
        if not gene_parser.is_file_uploaded:
            gene_parser.is_file_uploaded = True
            async_job = AsyncJob.produce_job(
                async_task_func=process_genes,
                job_payload={
                    'gene_parser_id': str(gene_parser.id),
                }
            )
            gene_parser.async_job = async_job
            gene_parser.save()

        return Response(
            status=status.HTTP_201_CREATED,
            data=GeneParserSerializer(gene_parser).data
        )
