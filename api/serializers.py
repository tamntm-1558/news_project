from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Article, Comment, Tag, ArticleHistory
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Login Custom serializer for JWT token generation
class CustomLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra data to the response (optional)
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['bio'] = self.user.bio
        data['token'] = self.user.token

        return data

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

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
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
    tagList = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()
    favoriteCount = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'description',
                'body', 'tagList', 'favorited', 'favoriteCount', 'author',
                'views_count', 'created_at', 'updated_at']
        read_only_fields = ['author', 'views_count']
        extra_kwargs = {
            'description': {'required': False},
        }

    def get_tagList(self, obj):
        return [tag.name for tag in obj.tag.all()]

    def get_favoriteCount(self, obj):
        return obj.favorites.count()

    def get_favorited(self, obj):
        return self.get_favoriteCount(obj) > 0

class ArticleHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleHistory
        fields = ['id', 'slug', 'title', 'description', 'body', 'updated_at']
        read_only_fields = ['id', 'updated_at']