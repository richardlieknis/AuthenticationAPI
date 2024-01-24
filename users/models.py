from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=50, default='Anonymous')
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254)
    # image = models.ImageField(upload_to='images/', blank=True)
    image = models.CharField(max_length=1023, blank=True)
    location = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=12, blank=True)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
