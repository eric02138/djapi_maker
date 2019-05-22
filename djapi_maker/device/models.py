from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField('created', auto_now_add=True)
    modified = models.DateTimeField('modified', auto_now=True)
