from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from .models import User, Article, Comment, Tag, Favorite

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'token', 'bio', 'image']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')

        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'token', 'username', 'bio', 'image']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'bio', 'image', 'following']

class CommentSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'body', 'article', 'author', 'created_at', 'updated_at']
        # use read_only_fields to: get field article', 'author' when get, but not required when post
        read_only_fields = ['article', 'author']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']
class ArticleSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    tag = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'description',
                'body', 'tag', 'author',
                'created_at', 'updated_at']
        read_only_fields = ['article', 'author']
        extra_kwargs = {
            'slug': {'required': False},
            'title': {'required': False},
            'description': {'required': False},
            'body': {'required': False}
        }

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'article', 'created_at']
