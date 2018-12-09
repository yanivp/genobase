from django.db import models


class BaseModel(models.Model):
    class Meta(object):
        abstract = True

    created_at = models.DateTimeField(db_index=True, auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(db_index=True, auto_now_add=True, null=False, blank=False)
