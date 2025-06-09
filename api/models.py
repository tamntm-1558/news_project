from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    following = models.BooleanField(default=False)

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    favorited = models.BooleanField(default=False)
    favorites_count = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    articles = models.ManyToManyField(Article, related_name='tags')
