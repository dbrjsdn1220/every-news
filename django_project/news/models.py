from django.db import models
from pgvector.django import VectorField
from django.contrib.auth.models import User

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
    views = models.IntegerField(default=0)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'article')


class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)