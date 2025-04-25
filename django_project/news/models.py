from django.db import models
from pgvector.django import VectorField

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    write_date = models.DateTimeField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    url = models.CharField(max_length=200, unique=True)
    keywords = models.JSONField(default=list)
    embedding = VectorField(dimensions=1536)