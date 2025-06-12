from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import (
    UserSerializer,
    ArticleSerializer,
    TagSerializer,
    CommentSerializer
)
from .models import User, Article, Comment, Tag, Favorite

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_queryset(self):
        username = self.kwargs.get('username')
        return User.objects.filter(username=username)

class ArticleViewSet(viewsets.ModelViewSet):
    # use select_related (1-1 or 1-n) and prefetch_related (n-n) avoid N+1 query: to optimize query
    queryset = Article.objects.all().select_related('author').prefetch_related('tag')
    serializer_class = ArticleSerializer
    # TODO: handle update check authen
    # permission_classes = [IsAuthenticatedOrReadOnly]

# TODO: remove block cmt
# class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Article.objects.select_related('author', 'tag')
#     serializer_class = ArticleSerializer

    # permission_classes = [IsAuthenticated]

    # def perform_update(self, serializer):
    #     serializer.save(author=self.request.user)
    # def perform_destroy(self, instance):
    #     instance.delete()

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        article_id = self.kwargs.get('article_id')
        return Comment.objects.filter(article=article_id).select_related('author')

    def perform_create(self, serializer):
        # TODO: update author_id login
        author_id = 1
        author = get_object_or_404(User, id=author_id)
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, id=article_id)
        serializer.save(article=article, author=author)

class TagListView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Extract the 'name' field from each tag
        tag_names = queryset.values_list('name', flat=True)
        return Response(tag_names)
    # TODO: handle update check authen. Create, update, delete item
    # permission_classes = [IsAuthenticatedOrReadOnly]