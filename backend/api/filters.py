from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from food.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = "name"


class RecipeFilter(FilterSet):
    """Фильтр выборки рецептов по определенным полям."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__author=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__author=self.request.user)
        return queryset
