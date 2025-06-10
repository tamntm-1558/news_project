from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import (
    UserSerializer,
    ArticleSerializer,
    TagSerializer,
    ArticleListSerializer,
    ArticleCommentSerializer
)
from .models import User, Article, Comment, Tag, Favorite

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ArticleListView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    # TODO: handle update check authen
    # permission_classes = [IsAuthenticatedOrReadOnly]

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.select_related('author')
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    # TODO: handle update check authen. Create, update, delete item
    # permission_classes = [IsAuthenticated]

    # def perform_update(self, serializer):
    #     serializer.save(author=self.request.user)
    # def perform_destroy(self, instance):
    #     instance.delete()

class ArticleCommentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects
    serializer_class = ArticleCommentSerializer
    lookup_field = 'slug'

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