from typing import Any, Optional, Union

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Categorie, Comment, Genre, Review, Title, User

from .filters import TitleFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsSelfOrAdmin
from .serializers import (
    CatigoriesSerializer,
    CommentsSerializer,
    GenresSerializer,
    MyTokenObtainPairSerializer,
    ReviewsSerializer,
    TitlesSerializer,
    TitleWriteSerializer,
    UserSerializer,
)
from .core import ViewSet


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination

    def title(self: 'ReviewsViewSet') -> Title:
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self: 'ReviewsViewSet') -> QuerySet[Review]:
        return Review.objects.filter(title=self.title())

    def perform_create(
        self: 'ReviewsViewSet',
        serializer: serializers.ModelSerializer,
    ) -> None:
        serializer.save(author=self.request.user, title=self.title())


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    pagination_class = CustomPagination
    search_fields = ('title_id',)

    def get_serializer_class(
        self: 'TitlesViewSet',
    ) -> serializers.ModelSerializer:
        if self.action in ('list', 'retrieve'):
            return TitlesSerializer
        return TitleWriteSerializer


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination

    def review(self: 'CommentsViewSet') -> Review:
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self: 'CommentsViewSet') -> QuerySet[Comment]:
        return self.review().comment.all()

    def perform_create(
        self: 'CommentsViewSet',
        serializer: serializers.ModelSerializer,
    ) -> None:
        serializer.save(author=self.request.user, review=self.review())


class CategoriesViewSet(ViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CatigoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(ViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)
    lookup_field = 'slug'


class SignUpViewSet(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(
        self: 'SignUpViewSet',
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        username = request.data.get('username')
        email = request.data.get('email')

        try:
            user = User.objects.get(username=username, email=email)
            confirmation_code = user.generate_confirmation_code()
            user.save()
        except User.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(username=username, email=email)
            confirmation_code = user.generate_confirmation_code()
            user.save()

        send_mail(
            'Код подверждения.',
            f'Ваш код подверждения: {confirmation_code}',
            settings.EMAIL_FROM,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {
                'email': user.email,
                'username': user.username,
            },
            status=status.HTTP_200_OK,
        )


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(
        self: 'MyTokenObtainPairView',
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username:
            return Response(
                {'detail': 'Пожалуйста, предоставьте имя пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь с таким username не найден.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not confirmation_code:
            return Response(
                {'detail': 'Пожалуйста, предоставьте confirmation code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.confirmation_code != confirmation_code:
            return Response(
                {'detail': 'Неверный confirmation code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().post(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def get_current_user(
        self: 'MyTokenObtainPairView',
        request: Request,
    ) -> Response:
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                data=request.data,
                instance=request.user,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_permissions(self) -> list:
        if self.request.method == 'PATCH':
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_allowed_methods(
        self: 'MyTokenObtainPairView',
        detail: Optional[bool] = None,
    ):
        if self.request.method == 'GET' or self.request.method == 'PATCH':
            return ['GET', 'PATCH', 'HEAD', 'OPTIONS']
        return super().get_allowed_methods(detail=detail)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrAdmin,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'

    def create(
        self: 'UserViewSet',
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        self.check_permissions(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(
        self: 'UserViewSet',
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Union[Response, HttpResponse]:
        if not kwargs.get('partial', False):
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
    def get_current_user(self: 'UserViewSet', request: Request) -> Response:
        if request.method == 'DELETE':
            raise MethodNotAllowed('DELETE')
        if request.user.is_authenticated:
            if request.method == 'PATCH':
                serializer = self.get_serializer(
                    data=request.data,
                    instance=request.user,
                    partial=True,
                    context={'change_self': True},
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response(
            {'detail': 'Пользователь не авторизован.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
