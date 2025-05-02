from django.urls import path
from . import views

urlpatterns = [
    path("", views.article_list),
    path("<str:type>/", views.genre_article_list),
    path("detail/<int:id>/", views.article_detail),  
    path("detail/<int:id>/related/", views.related_articles),
]