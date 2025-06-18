import django_filters
from .models import Article

class ArticleFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='iexact')
    favorited = django_filters.CharFilter(method='filter_favorited')
    tag = django_filters.CharFilter(field_name='tag__name', lookup_expr='iexact')
    createdBefore = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    createdAfter = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = Article
        fields = ['author', 'favorited', 'tag', 'createdBefore', 'createdAfter']

    def filter_favorited(self, queryset, name, value):
        return queryset.filter(favorites__user__username__iexact=value)
