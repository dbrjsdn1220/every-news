from rest_framework import serializers
from .models import Article, Like


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ['embedding']

class LikeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'