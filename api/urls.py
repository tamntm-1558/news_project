from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileView, ArticleListView, ArticleDetailView, ArticleCommentView, TagListView

router = DefaultRouter()

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/comments/', ArticleCommentView.as_view(), name='article-comments'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]