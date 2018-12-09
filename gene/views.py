from rest_framework.viewsets import ModelViewSet
from gene.models import Gene
from gene.serializers import GeneSerializer


class GeneParserViewSet(ModelViewSet):
    serializer_class = GeneSerializer
    queryset = Gene.objects.all()
