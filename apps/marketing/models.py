from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='news/')
    publish_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Banner(models.Model):
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Banner {self.id}'

class SMSLog(models.Model):
    message = models.TextField()
    total_sent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'SMS {self.id} on {self.created_at.date()}'
