from django.db import models
from datetime import datetime

# Create your models here.


class Address(models.Model):
    ip = models.CharField(max_length=30, primary_key=True)
    city = models.CharField(max_length=30)
    address = models.CharField(max_length=1024)

    def __str__(self):
        return self.ip


class Visit(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.ForeignKey("Address", on_delete=models.CASCADE)
    path = models.CharField(max_length=1024)
    date = models.DateTimeField(default=datetime.now, blank=True)
    UA = models.CharField(max_length=1024)

    def __str__(self):
        return self.path
