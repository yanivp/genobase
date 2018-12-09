import uuid
from django.db import models
from base.models import BaseModel
from gene_parser.models import GeneParser


class Gene(BaseModel):
    class Meta:
        index_together = [
            ('gene_parser', 'name'),
        ]

    id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True, primary_key=True)
    gene_parser = models.ForeignKey(
        GeneParser, related_name='gene_parsers', on_delete=models.CASCADE, null=False, db_index=True
    )
    name = models.CharField(null=False, max_length=255, db_index=True)
    sequence = models.TextField(null=False)
