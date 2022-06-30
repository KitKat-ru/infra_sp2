import rest_framework.permissions as rest_permissions
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, mixins, response, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from reviews import models
from users.models import User

from . import permissions, serializers
from .filters import TitleFilter


class ListCreateDestroyViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """Кастомный класс для чтения, создания и удаления объектов."""
    pass


class UserCreateViewSet(generics.CreateAPIView):
    """Представление для создания пользователя. Имеет только POST запрос.
    """
    permission_classes = (rest_permissions.AllowAny,)
    serializer_class = serializers.UserCreateSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = serializers.UserCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = get_object_or_404(
            User,
            username=serializer.data['username']
        )

        send_mail(
            'Добро пожаловать на YaMDB',
            f'Дорогой {user.username},\n'
            f'Ваш confirmation_code: {user.confirmation_code}',
            settings.POST_EMAIL,
            [f'{user.email}'],
            fail_silently=False,
        )

        return response.Response(
            data={
                'email': serializer.data['email'],
                'username': serializer.data['username']
            },
            status=status.HTTP_200_OK
        )


class CustomTokenObtain(generics.CreateAPIView):
    """Представление для создания JWT токена. Имеет только POST запрос.
    """
    permission_classes = (rest_permissions.AllowAny,)
    serializer_class = serializers.CustomTokenObtainSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = serializers.CustomTokenObtainSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.data['username']
        )

        token = serializer.get_token(user)

        return response.Response(
            {'token': f"{ token['access'] }"},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет Пользователя.
    Реализованы методы чтения, создания,
    частичного обновления и удаления объектов.
    Есть поиск по полю username.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.AdminOnly,)
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        url_name="me",
        serializer_class=serializers.UserSerializer,
        permission_classes=(
            rest_permissions.IsAuthenticated,
        ),
    )
    def me(self, request):
        """Доступ пользователя к своей учетной записи по '/users/me/'."""
        me_user = request.user
        serializer = self.get_serializer(me_user)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                me_user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(email=me_user.email, role=me_user.role)
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    """Вьюсет Категории.
    Реализованы методы чтения, создания и удаления объектов.
    Есть поиск по названию.
    """
    lookup_field = 'slug'
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (permissions.AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет Жанры.
    Реализованы методы чтения, создания и удаления объектов.
    Есть поиск по названию.
    """
    lookup_field = 'slug'
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (permissions.AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет Произведения.
    Реализованы методы чтения, создания,
    частичного обновления и удаления объектов.
    Есть фильтр по полям slug категории/жанра, названию, году.
    """
    queryset = models.Title.objects.annotate(rating=Avg("reviews__score"))
    permission_classes = (permissions.AdminOrReadOnly, )
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет Отзывы.
    Реализованы методы чтения, создания,
    частичного обновления и удаления объектов.
    """
    serializer_class = serializers.ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        rest_permissions.IsAuthenticatedOrReadOnly,
        permissions.AuthorOrReadOnly
    )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(models.Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        """
        Поля author и title заполняются из данных запроса.
        """
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                models.Title,
                pk=self.kwargs.get('title_id')
            )
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет Комментарии.
    Реализованы методы чтения, создания,
    частичного обновления и удаления объектов.
    """
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        rest_permissions.IsAuthenticatedOrReadOnly,
        permissions.AuthorOrReadOnly
    )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(models.Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        """
        Поля author и review заполняются из данных запроса.
        """
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                models.Review,
                pk=self.kwargs.get('review_id')
            )
        )
