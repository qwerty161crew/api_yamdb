from django_filters import rest_framework as filters

from reviews.models import Title


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class TitleFilter(filters.FilterSet):
    """
    Кастомный фильтр для модели Произведений
    для поиска жанра по слагу.
    """

    genre = CharFilterInFilter(
        field_name='genre__slug', lookup_expr='in'
    )
    category = CharFilterInFilter(
        field_name='categories__slug', lookup_expr='in'
    )
    year = filters.NumberFilter(
        field_name='year',
    )
    name = CharFilterInFilter(
        field_name='name', lookup_expr='in'
    )

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']