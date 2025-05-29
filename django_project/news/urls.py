from django.urls import path
from . import views

urlpatterns = [
    # 기사 관련
    path("news/", views.article_list),  # 전체 기사
    path("news/category/<str:type>/", views.genre_article_list),  # 카테고리 별 기사
    path("news/<int:article_id>/", views.article_detail),  # 기사 상세
    path("news/<int:article_id>/commented/", views.article_commented),  # 기사에 달린 댓글
    path("news/<int:article_id>/related/", views.article_detail_related),  # 관련 기사
    path("news/<int:article_id>/highlighted/", views.get_article_highlights),  # 기사의 하이라이트 목록
    path("news/<int:article_id>/highlight/", views.create_highlight),  # 하이라이트 생성
    path("news/<int:highlight_id>/delete/", views.delete_highlight),  # 하이라이트 삭제
    path("news/search/", views.search_articles),  # 뉴스 검색

    # 사용자 관련
    path("user/like/<int:article_id>/", views.like_article),  # 기사 좋아요
    path("user/comment/<int:article_id>/", views.comment_article),  # 기사에 댓글 달기
    path("user/information/", views.get_user_information),  # 유저 요약 활동 정보
    path("user/liked/", views.article_list_whom_liked),  # 해당 유저가 좋아요한 기사 목록
    path("user/viewed/", views.article_list_whom_viewed),  # 해당 유저가 읽은 기사 목록
    path("user/recommend/", views.recommend_articles_for_user),  # 해당 유저를 위한 추천 기사 목록
    
    # 챗봇 관련
    path("chatbot/<int:article_id>/", views.ChatbotView.as_view(), name="chatbot"),  # 챗봇 API
    path("chatbot/<int:article_id>/reset/", views.ChatbotResetView.as_view(), name="chatbot_reset"),  # 챗봇 초기화 API
]
