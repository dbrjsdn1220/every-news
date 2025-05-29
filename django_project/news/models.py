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


class LikeHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')


class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField()


class Highlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()  # 하이라이트된 텍스트
    start_offset = models.IntegerField()  # 하이라이트 시작 위치
    end_offset = models.IntegerField()  # 하이라이트 끝 위치
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'article', 'start_offset', 'end_offset')  # 중복 하이라이트 방지
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s highlight in {self.article.title}"
    

class CommentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    commented_at = models.DateTimeField(auto_now_add=True)