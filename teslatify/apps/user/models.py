from django.db import models

from django.contrib.auth.models import AbstractUser

from teslatify.apps.core.models import Base


class User(AbstractUser, Base):
    tesla_access_token = models.CharField(max_length=255, null=True, blank=True)
    tesla_refresh_token = models.CharField(max_length=255, null=True, blank=True)
    spotify_id = models.CharField(max_length=255, null=True, blank=True)
    spotify_access_token = models.CharField(max_length=255, null=True, blank=True)
    spotify_refresh_token = models.CharField(max_length=255, null=True, blank=True)
