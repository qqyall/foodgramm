from urllib.parse import urlparse, urlunparse

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import IsAdminIsAuthorOrReadOnly
from api.services import shopping_cart
from food.models import (Favorite, Ingredient, Recipe, ShoppingCart, Subscribe,
                         Tag, User)

from .constants import API_POS, GET_LINK_POS
from .mixins import ListRetrieveViewSet
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateDeleteSerilizer,
                          RecipeListSerializer, ShoppingCartSerializer,
                          ShortLinkSerializer,
                          SubscribeListCreateDeleteSerializer, TagSerializer)


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюсет для модели ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    serializer_class = RecipeCreateUpdateDeleteSerilizer

    actions = {
        ShortLinkSerializer: ("get_link",),
        FavoriteSerializer: ("favorite",),
        ShoppingCartSerializer: ("shopping_cart",),
        RecipeListSerializer: SAFE_METHODS,
    }

    def get_serializer_class(self):
        for serializer, actions in RecipeViewSet.actions.items():
            if self.action in actions:
                return serializer
        return RecipeViewSet.serializer_class

    @staticmethod
    def create_delete_template(request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        return recipe, user

    @staticmethod
    def create_template(request, pk, serializers, model):
        recipe, user = RecipeViewSet.create_delete_template(request, pk)
        if model.objects.filter(author=user, recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже добавлен!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = serializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete_template(request, pk, model):
        recipe, user = RecipeViewSet.create_delete_template(request, pk)
        if model.objects.filter(author=user, recipe=recipe).exists():
            model.objects.filter(author=user, recipe=recipe).delete()
            return Response(
                "Рецепт успешно удалён из списка покупок.",
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"errors": "Страница не найдена"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=("POST",),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, *args, **kwargs):
        """
        Получить / Добавить / Удалить  рецепт
        из избранного у текущего пользоватля.
        """
        return self.create_template(
            request,
            self.kwargs.get("pk"),
            self.get_serializer_class(),
            Favorite,
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, *args, **kwargs):
        return self.delete_template(request, self.kwargs.get("pk"), Favorite)

    @action(
        detail=True,
        methods=("POST",),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, *args, **kwargs):
        """
        Получить / Добавить / Удалить  рецепт
        из списка покупок у текущего пользоватля.
        """
        return self.create_template(
            request,
            self.kwargs.get("pk"),
            self.get_serializer_class(),
            ShoppingCart,
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, *args, **kwargs):
        return self.delete_template(
            request, self.kwargs.get("pk"), ShoppingCart
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """
        Скачать список покупок для выбранных рецептов,
        данные суммируются.
        """
        author = User.objects.get(id=self.request.user.pk)
        if author.shopping_cart.exists():
            return shopping_cart(self, request, author)
        return Response(
            "Список покупок пуст.", status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def get_long_url(uri):
        if not isinstance(uri, str) or not uri:
            raise ValueError(f"Получена пустая строка в uri - {uri}")

        parsed_uri = urlparse(uri)
        path_parts = parsed_uri.path.split("/")

        if not (
            (path_parts[API_POS], path_parts[GET_LINK_POS])
            == ("api", "get-link")
        ):
            raise ValueError(f"uri неправильного формата - {path_parts}")

        path_parts.pop(GET_LINK_POS)
        path_parts.pop(API_POS)
        long_url = "/".join(path_parts)

        return urlunparse(parsed_uri._replace(path=long_url))

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=(AllowAny,),
        url_path="get-link",
    )
    def get_link(self, request, **kwargs):
        """Получить короткую ссылку на рецепт"""
        request.data["long_url"] = RecipeViewSet.get_long_url(
            request.build_absolute_uri()
        )
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token, status_code = serializer.create(
                validated_data=serializer.validated_data
            )
            return Response(
                ShortLinkSerializer(token).data, status=status_code
            )
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class SubscribeViewSet(ListRetrieveViewSet):
    """Вьюсет для модели подписок."""

    queryset = Subscribe.objects.all()
    serializer_class = SubscribeListCreateDeleteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination


class ShortLinkAPIView(APIView):
    """Вьюсет для модели коротких ссылок."""
