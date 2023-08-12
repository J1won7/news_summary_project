from django.db import models


class News(models.Model):
    newsid = models.IntegerField(primary_key=True)
    category = models.IntegerField()
    title = models.CharField(max_length=50)
    image = models.CharField(max_length=200)
    summary = models.TextField()
    write_time = models.CharField(max_length=20)
    url = models.CharField(max_length=50)
