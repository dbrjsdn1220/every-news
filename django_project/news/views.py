from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Article, LikeHistory, ViewHistory, Highlight, CommentHistory
from .serializers import (
    ArticleListSerializer, LikeListSerializer, ViewListSerializer, CommentListSerializer
)
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from pgvector.django import CosineDistance
from django.db.models import Count
from django.utils import timezone
import numpy as np
from elasticsearch import Elasticsearch
import ollama
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


# 전체 기사 리스트
@api_view(['GET'])
def article_list(request):
	sort_by = request.GET.get('sort', '-write_date')  # 기본값은 최신순
	articles = Article.objects \
        .annotate(like_count=Count('likehistory'), comment_count=Count('commenthistory'))
	

	# 정렬 옵션에 따른 처리
	if sort_by == 'likes':
		articles = articles.order_by('-like_count', '-write_date')
	elif sort_by == 'views':
		articles = articles.order_by('-views', '-write_date')
	else:  # 기본값 또는 '-write_date'
		articles = articles.order_by('-write_date')
	
	serializer = ArticleListSerializer(articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)


# 장르 전체 기사 리스트
@api_view(['GET'])
def genre_article_list(request, type):
	sort_by = request.GET.get('sort', '-write_date')  # 기본값은 최신순
	articles = Article.objects.filter(category=type)\
		.annotate(like_count=Count('likehistory'), comment_count=Count('commenthistory'))
	
	# 정렬 옵션에 따른 처리
	if sort_by == 'likes':
		articles = articles.order_by('-like_count', '-write_date')
	elif sort_by == 'views':
		articles = articles.order_by('-views', '-write_date')
	else:  # 기본값 또는 '-write_date'
		articles = articles.order_by('-write_date')
	
	serializer = ArticleListSerializer(articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)


# 기사 자세히
@api_view(['GET'])
@permission_classes([AllowAny]) 
def article_detail(request, article_id):
	article = Article.objects \
        .annotate(like_count=Count('likehistory'), comment_count=Count('commenthistory')) \
        .get(id=article_id)
	article.views += 1
	article.save(update_fields=['views'])
	liked = False

	# 로그인된 사용자일 때만 ViewHistory 생성
	if request.user.is_authenticated:
		ViewHistory.objects.update_or_create(
			user_id=request.user.id, 
			article_id=article.id,
			defaults={'viewed_at': timezone.now()}
		)
		liked = LikeHistory.objects.filter(user_id=request.user.id, article_id=article_id).exists()

	serializer = ArticleListSerializer(article)
	return Response({'data': serializer.data, 'liked': liked}, status=status.HTTP_200_OK)
	

# 기사에 달린 댓글
@api_view(['GET'])
def article_commented(request, article_id):
    comments = CommentHistory.objects.filter(article_id=article_id)
    serializer = CommentListSerializer(comments, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


# 기사 내용 기반 관련 기사 TOP5
@api_view(['GET'])
def article_detail_related(request, article_id):
	article = Article.objects.get(id=article_id)

	related_articles = Article.objects.exclude(id=article.id)\
		.annotate(similarity=CosineDistance('embedding', article.embedding))\
		.order_by('similarity')[:5]  # 코사인 거리가 가까운 순으로 5개

	serializer = ArticleListSerializer(related_articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)
	

# 기사 좋아요 누르기
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_article(request, article_id):
    user_id = request.user.id
    liked = LikeHistory.objects.filter(user_id=user_id, article_id=article_id)
    
    # 좋아요가 있으면 취소
    if liked.exists():
        liked.delete()
        status_code = status.HTTP_200_OK
        liked = False
    # 없으면 생성
    else:
        LikeHistory.objects.create(user_id=user_id, article_id=article_id)
        status_code = status.HTTP_201_CREATED
        liked = True

    count = LikeHistory.objects.filter(article_id=article_id).count()
    return Response({'like_count':count, 'liked':liked}, status_code)


# 기사에 댓글 달기
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_article(request, article_id):
    user_id = request.user.id
    comment = request.data.get('comment', '')
    
    CommentHistory.objects.create(
        user_id=user_id, 
        article_id=article_id,
        comment=comment
    )
    status_code = status.HTTP_201_CREATED

    count = CommentHistory.objects.filter(article_id=article_id).count()
    return Response({'comment': comment, 'comment_count': count}, status_code)
	

# 유저 정보
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_information(request):
    user_id = request.user.id
    
    total_like = LikeHistory.objects.filter(user_id=user_id).count()
    total_comment = CommentHistory.objects.filter(user_id=user_id).count()
    total_highlight = Highlight.objects.filter(user_id=user_id).count()
    total_attendance = ViewHistory.objects.filter(user_id=user_id) \
        .annotate(day=TruncDate('viewed_at')) \
        .values('day') \
        .distinct() \
        .count()

    return Response({
        'total_like': total_like,
        'total_comment': total_comment,
        'total_highlight': total_highlight,
        'total_attendance': total_attendance,
    }, status=status.HTTP_200_OK)


# 사용자가 좋아요 누른 기사 리스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def article_list_whom_liked(request):
    user_id = request.user.id

    liked_articles = LikeHistory.objects.filter(user_id=user_id)
    serializer = LikeListSerializer(liked_articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 사용자가 읽은 기사 리스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def article_list_whom_viewed(request):
	user_id = request.user.id
	
	viewed_articles = ViewHistory.objects.filter(user_id=user_id)
	serializer = ViewListSerializer(viewed_articles, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)


# 사용자 추천 기사
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_articles_for_user(request):
	LIKE_WEIGHT = 3.0
	VIEW_WEIGHT = 1.0
	user_id = request.user.id

	# 1. 유저의 좋아요 및 조회 기사 ID 수집
	liked_article_ids = LikeHistory.objects.filter(user_id=user_id).values_list('article_id', flat=True)
	viewed_article_ids = ViewHistory.objects.filter(user_id=user_id).values_list('article_id', flat=True)
	exclude_ids = set(liked_article_ids).union(set(viewed_article_ids))

	# 2. 유저 임베딩 계산 (가중 평균)
	weighted_vectors = []
	
	liked_articles = Article.objects.filter(id__in=liked_article_ids)
	for article in liked_articles:
		if article.embedding is not None and len(article.embedding) > 0:
			weighted_vectors.append((np.array(article.embedding), LIKE_WEIGHT))

	viewed_articles = Article.objects.filter(id__in=viewed_article_ids)
	for article in viewed_articles:
		if article.embedding is not None and len(article.embedding) > 0:
			weighted_vectors.append((np.array(article.embedding), VIEW_WEIGHT))

	vectors = np.array([vec * weight for vec, weight in weighted_vectors])
	weights = np.array([weight for _, weight in weighted_vectors])
	user_embedding = np.sum(vectors, axis=0) / np.sum(weights)

    # 3. 추천 기사 조회 (유사도 기반)
	recommendations = Article.objects.exclude(id__in=exclude_ids)\
        .annotate(similarity=CosineDistance('embedding', user_embedding))\
        .order_by('similarity')

    # 4. 직렬화 후 응답
	serializer = ArticleListSerializer(recommendations, many=True)
	return Response(serializer.data, status=status.HTTP_200_OK)


# 검색
@api_view(['GET'])
def search_articles(request):
    query = request.GET.get('q', '')
    if not query:
        return Response({"results": []})

    es = Elasticsearch("http://localhost:9200")
    
    # 검색 쿼리 구성
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content", "keywords"]
            }
        }
    }
    
    try:
        # 검색 실행
        response = es.search(
            index="news",
            body=search_body
        )
        
        # 검색 결과를 직렬화
        results = []
        for hit in response["hits"]["hits"]:
            data = hit["_source"]
            like_count = LikeHistory.objects.filter(article_id=data["id"]).count()
            views = Article.objects.get(id=data["id"]).views

            results.append({
                "id": data["id"],
                "title": data["title"],
                "writer": data["writer"],
                "category": data["category"],
                "write_date": data["write_date"],
                "content": data["content"][:200] + "..." if len(data["content"]) > 200 else data["content"],
                "url": data["url"],
                "keywords": data["keywords"],
                "views": views,
                "like_count": like_count,
                "score": hit["_score"]
            })

        return Response({
            "total": response["hits"]["total"]["value"],
            "results": results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"검색 중 에러 발생: {str(e)}")
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotView(APIView):
    def post(self, request, article_id):
        if not request.user.is_authenticated:
            return Response({"message": "인증이 필요합니다."}, status=401)

        question = request.data.get("question")
        if not question:
            return Response({"message": "질문이 필요합니다."}, status=400)

        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"message": "기사를 찾을 수 없습니다."}, status=404)

        session_key = f"chat_history_{request.user.id}_{article_id}"

        # 초기 system 메시지 저장
        if session_key not in request.session:
            system_prompt = f"""당신은 뉴스 기사를 분석하고 설명해주는 AI 어시스턴트입니다.
            당신은 바쁜 현대인들이 기사를 보는 시간을 줄일 수 있도록 기사 내용을 이해하기 쉽고
            짧게 요약해서 제공해주는 역할을 합니다. 
            주어진 기사 내용을 바탕으로 사용자의 질문에 답변해주며 답변 글자 수는 200자 이내로 합니다.
            글자 수 제한을 꼭 지켜주세요.
            답변은 친절하고 전문적이어야 하며, 기사 내용에 기반해야 합니다.
            기사 내용에 없는 정보는 추측하지 마세요.
            그리고 답변은 plane text 형태로 제공해 주세요. 절대 절대 마크다운 형식으로 주면 안됩니다!

            제목: {article.title}
            작성일: {article.write_date}
            내용: {article.content}
            """
            request.session[session_key] = [
                {"role": "system", "content": system_prompt}
            ]

        # 사용자 메시지 추가
        history = request.session[session_key]
        history.append({"role": "user", "content": question})

        # Ollama 호출
        try:
            response = ollama.chat(
                model="exaone3.5:2.4b", 
                messages=history
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # 챗봇 응답 저장
        answer = response['message']['content']
        history.append({"role": "assistant", "content": answer})
        request.session[session_key] = history

        return Response({"response": answer})


# 챗봇 초기화
class ChatbotResetView(APIView):
    def post(self, request, article_id):
        if not request.user.is_authenticated:
            return Response({"message": "인증이 필요합니다."}, status=401)

        session_key = f"chat_history_{request.user.id}_{article_id}"
        if session_key in request.session:
            del request.session[session_key]

        return Response({"message": "대화 세션이 초기화되었습니다."}, status=200)


# 하이라이트 생성/수정
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_highlight(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({"error": "기사를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    text = request.data.get('text')
    start_offset = request.data.get('start_offset')
    end_offset = request.data.get('end_offset')

    if not all([text, start_offset is not None, end_offset is not None]):
        return Response({"error": "필수 필드가 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 중복 하이라이트 체크
    existing_highlight = Highlight.objects.filter(
        user=request.user,
        article=article,
        start_offset=start_offset,
        end_offset=end_offset
    ).first()

    if existing_highlight:
        return Response({"error": "이미 존재하는 하이라이트입니다."}, status=status.HTTP_400_BAD_REQUEST)

    highlight = Highlight.objects.create(
        user=request.user,
        article=article,
        text=text,
        start_offset=start_offset,
        end_offset=end_offset
    )

    return Response({
        "id": highlight.id,
        "text": highlight.text,
        "start_offset": highlight.start_offset,
        "end_offset": highlight.end_offset,
        "created_at": highlight.created_at
    }, status=status.HTTP_201_CREATED)

# 하이라이트 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_highlight(request, highlight_id):
    try:
        highlight = Highlight.objects.get(id=highlight_id, user=request.user)
        highlight.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Highlight.DoesNotExist:
        return Response({"error": "하이라이트를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

# 기사의 하이라이트 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_article_highlights(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response({"error": "기사를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    highlights = Highlight.objects.filter(user=request.user, article=article)
    return Response([{
        "id": h.id,
        "text": h.text,
        "start_offset": h.start_offset,
        "end_offset": h.end_offset,
        "created_at": h.created_at
    } for h in highlights], status=status.HTTP_200_OK)