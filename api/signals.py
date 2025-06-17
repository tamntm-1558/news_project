from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tag

@receiver([post_save, post_delete], sender=Tag)
def clear_tag_list_cache(sender, instance, **kwargs):
    cache_key = 'tag_list'
    cache.delete(cache_key)