import os
import codecs

from django.db import models


# create_default_hash function
def create_default_hash(length=12):
    return codecs.encode(os.urandom(length), 'hex').decode()


class Base(models.Model):
    hash_id = models.CharField(
        default=create_default_hash,
        editable=False,
        max_length=30
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
