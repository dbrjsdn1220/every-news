from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Article, Like
from .serializers import ArticleListSerializer, LikeListSerializer
from django.contrib.auth.models import User



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

# 특정 기사 자세히
@api_view(['GET'])
def article_detail(request, article_id):
	if request.method == 'GET':
		article = Article.objects.get(id=article_id)
		serializer = ArticleListSerializer(article)
		return Response(serializer.data, status=status.HTTP_200_OK)

# 같은 장르의 기사 5개
@api_view(['GET'])
def related_articles(request, article_id):
	if request.method == 'GET':
		current_article = Article.objects.get(id=article_id)
		related = Article.objects.filter(category=current_article.category).exclude(id=id)[:5]
		serializer = ArticleListSerializer(related, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
# 특정 기사 좋아요 누르기
@api_view(['POST'])
def user_like_article(request):
	if request.method == 'POST':
		user_id = request.POST.get('user_id')
		article_id = request.POST.get('article_id')
		
		exists = Like.objects.filter(user_id=user_id, article_id=article_id).exists()
		if exists:
			return Response({'message': 'Already liked'}, status=status.HTTP_200_OK)
		
		Like.objects.create(user_id=user_id, article_id=article_id)
		return Response({'message': 'Like added'}, status=status.HTTP_201_CREATED)
	
# 사용자가 누른 좋아요 리스트
@api_view(['GET'])
def user_liked_articles_list(request, user_id):
	if request.method == 'GET':
		liked_articles = Like.objects.filter(user_id=user_id)
		serializer = LikeListSerializer(liked_articles, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	
# 특정 기사에 좋아요 누른 유저 리스트
@api_view(['GET'])
def article_liked_users_list(request, article_id):
	if request.method == 'GET':
		liked_users = Like.objects.filter(article_id=article_id)
		serializer = LikeListSerializer(liked_users, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)