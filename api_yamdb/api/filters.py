from django_filters import rest_framework

from reviews import models


class TitleFilter(rest_framework.FilterSet):
    """Фильтр для Произведений.
    Доступен фильтр по жанру, категории, названию и году.
    """
    genre = rest_framework.CharFilter(field_name='genre__slug')
    category = rest_framework.CharFilter(field_name='category__slug')
    name = rest_framework.CharFilter(
        field_name='name', lookup_expr='icontains')
    year = rest_framework.NumberFilter(field_name='year')

    class Meta:
        model = models.Title
        fields = ['genre', 'category', 'name', 'year']
