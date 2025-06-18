from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    UserRetrieveUpdateView,
    ProfileView,
    ArticleViewSet,
    CommentListCreateView,
    CommentDetailView,
    TagListView,
    favorite_article,
    FeedView,
    follow_user
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='articles')

urlpatterns = [
    path('user/register/', RegisterView.as_view(), name='user-register'),
    path('user/login/', LoginView.as_view(), name='user-login'),
    path('user/', UserRetrieveUpdateView.as_view(), name='user-detail-update'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('articles/<int:article_id>/comments/', CommentListCreateView.as_view(), name='comments-list-create'),
    path('articles/<int:article_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='comments-detail'),
    path('articles/<int:article_id>/favorite/', favorite_article, name='favorite-article'),
    path('articles/feed/', cache_page(60)(FeedView.as_view()), name='feed-articles'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/follow/', follow_user, name='profile-follow'),
    path('', include(router.urls)),
]
