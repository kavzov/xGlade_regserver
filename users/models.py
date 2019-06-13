from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator


class User(AbstractUser):
    wallet = models.DecimalField(blank=True, max_digits=10, decimal_places=4, default=250.0)
    battles = models.PositiveIntegerField(blank=True, default=0)
    won = models.PositiveIntegerField(blank=True, default=0)
    rating = models.PositiveIntegerField(blank=True, default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
