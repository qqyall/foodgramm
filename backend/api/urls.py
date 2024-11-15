from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)

urlpatterns = [
    re_path("auth/", include("djoser.urls")),  # Работа с пользователями
    re_path("auth/", include("djoser.urls.authtoken")),  # Работа с токенами
    path("", include(router.urls)),
]
