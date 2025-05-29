from rest_framework import serializers
from .models import Article, LikeHistory, ViewHistory, CommentHistory
from django.contrib.auth.models import User


class ArticleListSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        exclude = ['embedding']

class LikeListSerializer(serializers.ModelSerializer):
    article = ArticleListSerializer()

    class Meta:
        model = LikeHistory
        fields = '__all__'

class ViewListSerializer(serializers.ModelSerializer):
    article = ArticleListSerializer()
    
    class Meta:
        model = ViewHistory
        fields = '__all__'

class CommentListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CommentHistory
        fields = '__all__'