from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, ShortLink, Subscribe, Tag)


class IngredientsInline(admin.TabularInline):
    """
    Админ-зона для интеграции добавления ингридиентов в рецепты.
    Сразу доступно добавление 3х ингрдиентов.
    """

    model = IngredientRecipe
    extra = 3


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админ-зона подписок."""

    list_display = ("user", "author")
    list_filter = ("author",)
    search_fields = ("user",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона избранных рецептов."""

    list_display = ("author", "recipe")
    list_filter = ("author",)
    search_fields = ("author",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-зона покупок."""

    list_display = ("author", "recipe")
    list_filter = ("author",)
    search_fields = ("author",)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админ-зона ингридентов для рецептов."""

    list_display = (
        "id",
        "recipe",
        "ingredient",
        "amount",
    )
    list_filter = ("recipe", "ingredient")
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона рецептов."""

    list_display = (
        "id",
        "author",
        "name",
        "in_favorite",
    )
    search_fields = ("name",)
    list_filter = ("author", "name", "tags")
    filter_horizontal = ("ingredients",)
    empty_value_display = "-пусто-"
    inlines = [IngredientsInline]

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = "Добавленные рецепты в избранное"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-зона тегов."""

    list_display = ("id", "name", "slug")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона ингридиентов."""

    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):
    """Админ-зона коротких ссылок."""

    list_display = ("long_url", "short_url", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("long_url", "short_url", "is_active", "created_at")
