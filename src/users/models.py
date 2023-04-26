from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from .managers import CustomManager
from ..core.models import Album
from config import settings


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=25, blank=True, null=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    year_birth = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    object = CustomManager()

    def __str__(self):
        return self.email

