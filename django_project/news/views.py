from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Article
from .serializers import ArticleListSerializer


# 전체 기사 리스트
@api_view(['GET'])
def article_list(request):
	if request.method == 'GET':
		articles = Article.objects.all()
		serializer = ArticleListSerializer(articles, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

# 특정 장르 전체 기사 리스트
@api_view(['GET'])
def genre_article_list(request, type):
	if request.method == 'GET':
		articles = Article.objects.filter(category=type)
		serializer = ArticleListSerializer(articles, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)