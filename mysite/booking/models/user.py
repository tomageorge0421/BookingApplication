from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    profile_picture_url = models.URLField(blank=True, null=True)
