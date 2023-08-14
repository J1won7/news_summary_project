from django.db import models


class News(models.Model):
    _id = models.IntegerField(primary_key=True)
    category = models.IntegerField()
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=150)
    summary = models.TextField()
    time = models.CharField(max_length=20)
    url = models.CharField(max_length=100)

    class Meta:
        ordering = ['-time']
        db_table = "news"

