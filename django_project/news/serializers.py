from rest_framework import serializers
from .models import Article, LikeHistory, ViewHistory


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ['embedding']

class LikedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeHistory
        fields = '__all__'

class ViewedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewHistory
        fields = '__all__'