from rest_framework import serializers
from .models import User, Article, Comment, Tag, Favorite

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'bio', 'image', 'following']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'body', 'article', 'author', 'created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tag = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'description',
                'body', 'tag', 'author',
                'created_at', 'updated_at']

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tag = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'description',
                'body', 'tag', 'author',
                'created_at', 'updated_at']

class ArticleCommentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'comments',
                'created_at', 'updated_at']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'article', 'created_at']
