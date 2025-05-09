from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Article, LikeHistory, ViewHistory
from .serializers import ArticleListSerializer, LikedListSerializer, ViewedListSerializer
from django.contrib.auth.models import User
from pgvector.django import CosineDistance


# 전체 기사 리스트
@api_view(['GET'])
def article_list(request):
	articles = Article.objects.all().order_by('-write_date')
	serializer = ArticleListSerializer(articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)

# 장르 전체 기사 리스트
@api_view(['GET'])
def genre_article_list(request, type):
	articles = Article.objects.filter(category=type).order_by('-write_date')
	serializer = ArticleListSerializer(articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)

# 기사 자세히
@api_view(['GET'])
@permission_classes([AllowAny]) 
def article_detail(request, article_id):
	article = Article.objects.get(id=article_id)
	article.views += 1
	article.save(update_fields=['views'])

	# 로그인된 사용자일 때만 ViewHistory 생성
	if request.user.is_authenticated:
		ViewHistory.objects.create(user_id=request.user.id, article_id=article.id)

	serializer = ArticleListSerializer(article)
	return Response(serializer.data, status=status.HTTP_200_OK)
	
# 기사 내용 기반 관련 기사 TOP5
@api_view(['GET'])
def article_detail_related(request, article_id):
	article = Article.objects.get(id=article_id)

	related_articles = Article.objects.exclude(id=article.id).annotate(
		similarity=CosineDistance('embedding', article.embedding)
	).order_by('-similarity')[:5]  # 유사도 기준 내림차순 5개

	serializer = ArticleListSerializer(related_articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)
	
# 기사 좋아요 누르기
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_article(request, article_id):
	user_id = request.user.id
	
	# 좋아요가 있으면 취소
	liked = LikeHistory.objects.filter(user_id=user_id, article_id=article_id)
	if liked.exists():
		liked.delete()
		return Response({'message': 'Like Canceled'}, status=status.HTTP_200_OK)
	
	# 없으면 생성
	LikeHistory.objects.create(user_id=user_id, article_id=article_id)
	return Response({'message': 'Like added'}, status=status.HTTP_201_CREATED)

# 기사에 좋아요 누른 유저 리스트
@api_view(['GET'])
def article_liked_user_list(request, article_id):
	liked_users = LikeHistory.objects.filter(article_id=article_id)
	serializer = LikedListSerializer(liked_users, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)
	
# 사용자가 좋아요 누른 기사 리스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_liked_article_list(request):
	print('test1')
	user_id = request.user.id

	liked_articles = LikeHistory.objects.filter(user_id=user_id)
	serializer = LikedListSerializer(liked_articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)
	
# 사용자가 읽은 기사 리스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_viewed_article_list(request):
	print('test2')
	user_id = request.user.id
	
	viewed_articles = ViewHistory.objects.filter(user_id=user_id)
	serializer = ViewedListSerializer(viewed_articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)