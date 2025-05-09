from rest_framework import serializers
from .models import Article, Like


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class LikeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'