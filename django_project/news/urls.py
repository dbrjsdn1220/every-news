from django.urls import path
from . import views

urlpatterns = [
    path("", views.article_list),
    path("<str:type>/", views.genre_article_list),
    path("detail/<int:article_id>/", views.article_detail),
    path("like/", views.user_like_article),
    path("like/user/<int:user_id>/", views.user_liked_articles_list),
    path("like/article/<int:article_id>/", views.article_liked_users_list),
]