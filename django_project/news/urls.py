from django.urls import path
from . import views

urlpatterns = [
    path("", views.article_list),
    path("liked/", views.user_liked_article_list),
    path("viewed/", views.user_viewed_article_list),
    path("<str:type>/", views.genre_article_list),  # 이게 먼저 나오면 liked, viewed를 str로 인식함
    path("detail/<int:article_id>/", views.article_detail),
    path("detail/<int:article_id>/related/", views.article_detail_related),
    path("detail/<int:article_id>/liked/", views.article_liked_user_list),
    path("like/<int:article_id>/", views.like_article),
]