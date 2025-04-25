from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Article
from .serializers import ArticleListSerializer
from django.http import JsonResponse


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


@api_view(['GET'])
def article_detail(request, id):
	if request.method == 'GET':
		article = Article.objects.get(id=id)
		serializer = ArticleListSerializer(article)
		return Response(serializer.data, status=status.HTTP_200_OK)

# views.py
@api_view(['GET'])
def related_articles(request, id):
        current_article = Article.objects.get(id=id)
        related = Article.objects.filter(category=current_article.category).exclude(id=id)[:5]
        serializer = ArticleListSerializer(related, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
