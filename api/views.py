from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    ArticleSerializer,
    TagSerializer,
    CommentSerializer
)
from .models import User, Article, Comment, Tag, Favorite

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_token = RefreshToken.for_user(user)
        token = refresh_token.access_token
        user.token = str(token)
        user.save(update_fields=['token'])
        return Response({
            'user': {
                **UserSerializer(user, context={'request': request}).data,
                'token': str(token),
            },
            'refresh_token': str(refresh_token),
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh_token = RefreshToken.for_user(user)
        token = refresh_token.access_token
        user.token = str(token)
        user.save(update_fields=['token'])
        return Response({
            'user': {
                **UserSerializer(user, context={'request': request}).data,
                'token': str(token),
            },
            'refresh_token': str(refresh_token),
        })

class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    # TODO: handle update check authen
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        # TODO: custom response format
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data.copy()
        allowed_fields = {'email', 'username', 'password', 'image', 'bio'}
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        serializer = self.get_serializer(user, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        if 'password' in update_data:
            user.set_password(update_data['password'])
            user.save(update_fields=['password'])
        serializer.save()
        return Response({'user': serializer.data})

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        profile_data = UserProfileSerializer(user, context={'request': request}).data
        return Response({
            "profile": profile_data
        })

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