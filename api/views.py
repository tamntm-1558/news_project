from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Subquery
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomLoginSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    ArticleSerializer,
    TagSerializer,
    CommentSerializer
)
from .models import User, Article, Comment, Tag, Favorite

## LoginView use TokenObtainPairView of rest_framework_simplejwt
# class LoginView(TokenObtainPairView):
#     serializer_class = CustomLoginSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

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

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

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

class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        profile_data = UserSerializer(user, context={'request': request}).data
        return Response({'user': profile_data})

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
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        tag_name = self.request.query_params.get('tag')
        if tag_name:
            queryset = queryset.filter(tag__name=tag_name)
        author_username = self.request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        print(f"Queryset after filtering: {queryset.query}")
        return queryset

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        article_id = self.kwargs.get('article_id')
        return Comment.objects.filter(article=article_id).select_related('author')

    def perform_create(self, serializer):
        author = self.request.user
        if not author.is_authenticated:
            raise PermissionDenied("You must be logged in to comment.")
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, id=article_id)
        serializer.save(article=article, author=author)


class TagListView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Extract the 'name' field from each tag
        tag_names = queryset.values_list('name', flat=True)
        return Response(tag_names)

class FavoriteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id, *args, **kwargs):
        article = get_object_or_404(Article, id=article_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, article=article)
        if created:
            return Response({'detail': 'Article favorited.'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Article already favorited.'}, status=status.HTTP_200_OK)

    def delete(self, request, article_id, *args, **kwargs):
        article = get_object_or_404(Article, id=article_id)
        favorite = Favorite.objects.filter(user=request.user, article=article)
        if favorite.exists():
            favorite.delete()
            return Response({'detail': 'Favorite removed.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Favorite does not exist.'}, status=status.HTTP_404_NOT_FOUND)

class FeedView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view your feed.")

        articles = Article.objects.filter(
            favorites__user=user
        ).order_by('-favorites__created_at')
        return articles
