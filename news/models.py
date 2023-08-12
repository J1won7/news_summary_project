from django.db import models


class News(models.Model):
    _id = models.IntegerField(primary_key=True)
    category = models.IntegerField()
    title = models.CharField(max_length=50)
    image = models.FilePathField(null=True)
    summary = models.TextField()
    write_time = models.CharField(max_length=20)
    url = models.FilePathField()

    class Meta:
        db_table = "news"
