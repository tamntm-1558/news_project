from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    following = models.BooleanField(default=False)

class Article(models.Model):
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    tag = models.ManyToManyField('Tag', related_name='articles', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    body = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')  # Ensure a user can favorite an article only once