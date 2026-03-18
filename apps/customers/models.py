from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    telegram = models.CharField(max_length=255, blank=True, null=True)
    points = models.IntegerField(default=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.phone}'
