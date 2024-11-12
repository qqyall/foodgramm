from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdminIsAuthor, IsAdminIsAuthorOrReadOnly
from api.serializers import SubscribeListCreateDeleteSerializer
from food.models import Subscribe
from users.models import User
from users.serializers import (SetPasswordSerrializer,
                               UserListRetrieveSerializer, UserSerializer,
                               UserUpdateAvatarSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset для модели пользователей."""

    queryset = User.objects.all()
    permission_classes = (IsAdminIsAuthor,)
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer

    actions = {
        UserListRetrieveSerializer: ("list", "retrieve", "me"),
        UserUpdateAvatarSerializer: ("avatar",),
        SetPasswordSerrializer: ("set_password",),
        SubscribeListCreateDeleteSerializer: ("subscriptions", "subscribe"),
    }

    def get_serializer_class(self):
        for serializer, actions in UserViewSet.actions.items():
            if self.action in actions:
                return serializer
        return UserViewSet.serializer_class

    def retrieve(self, request, *args, **kwargs):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=kwargs["pk"])
        seriazier = self.get_serializer_class()(
            user, context=self.get_serializer_context()
        )
        return Response(seriazier.data)

    @action(
        methods=("GET",),
        detail=False,
        url_path="me",
        url_name="me",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer_class()(
            request.user, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=("PUT",),
        detail=False,
        url_path="me/avatar",
        url_name="me/avatar",
        permission_classes=(IsAdminIsAuthorOrReadOnly, IsAuthenticated),
    )
    def avatar(self, request):
        serializer = self.get_serializer_class()(
            request.user,
            data=request.data,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = User.objects.filter(username=request.user)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("POST",), detail=False, permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            if user.check_password(serializer.data["current_password"]):
                self.request.user.set_password(
                    serializer.validated_data["new_password"]
                )
                self.request.user.save()
                return Response(
                    "Пароль успешно изменен", status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {"error": "Неверно указан текущий пароль"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=("GET",),
        detail=False,
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriptions = Subscribe.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer_class()(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @staticmethod
    def create_delete_template(request, pk):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        return author, user

    @action(
        methods=("POST",),
        detail=True,
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        author, user = UserViewSet.create_delete_template(request, pk)
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request, "author": author}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=author, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"errors": "Страница не найдена"}, status=status.HTTP_404_NOT_FOUND
        )

    @transaction.atomic
    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        author, user = UserViewSet.create_delete_template(request, pk)
        subscribe_object = Subscribe.objects.filter(author=author, user=user)
        if subscribe_object.exists():
            subscribe_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Подписка не найдена"},
            status=status.HTTP_400_BAD_REQUEST,
        )
