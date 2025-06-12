from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileView,
    ArticleViewSet,
    # ArticleListView,
    # ArticleDetailView,
    CommentListCreateView,
    TagListView
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='articles')

urlpatterns = [
    # path('articles', ArticleListView.as_view(), name='article-list'),
    # path('articles/<int:pk>', ArticleDetailView.as_view(), name='article-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('articles/<int:article_id>/comments/', CommentListCreateView.as_view(), name='comments-list-create'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]