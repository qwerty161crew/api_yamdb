from rest_framework import filters, mixins, viewsets, pagination, generics
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, IsAdminUser)
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnly, IsModerator, IsAdminOrReadOnly, IsSelfOrAdmin, IsOwnerOrReadOnly
from .pagination import CustomPagination

from reviews.models import Review, Title, Comment, Categorie, Genre, User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import MethodNotAllowed, ValidationError, NotFound
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter

from .serializers import ReviewsSerializers, TitlesSerializers, CommentsSerializers, CatigoriesSerializers, GenresSerializers, UserSerializer, MyTokenObtainPairSerializer, TitleWriteSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializers
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination

    def title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.title())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.title())


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    pagination_class = CustomPagination
    search_fields = ('title_id', )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitlesSerializers
        return TitleWriteSerializer


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializers
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination

    def review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.review().comment.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.review()
        )


class CategoriesViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CatigoriesSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', )
    lookup_field = 'slug'


class GenresViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', )
    lookup_field = 'slug'


class SignUpViewSet(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
    
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.email != email:
                return Response(
                    {'detail': 'A user with this username already exists with different email.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            confirmation_code = user.generate_confirmation_code()
            user.save()
            send_mail(
                'Код подтверждения.',
                f'Ваш код подтверждения: {confirmation_code}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response(
                {'email': user.email, 'username': user.username}, 
                status=status.HTTP_200_OK
            )
        else:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = User.objects.create(
                    email=serializer.validated_data['email'], 
                    username=serializer.validated_data['username']
                )
                confirmation_code = user.generate_confirmation_code()
                user.save()
                send_mail(
                    'Код подтверждения.',
                    f'Ваш код подтверждения: {confirmation_code}',
                    'from@example.com',
                    [user.email],
                    fail_silently=False,
                )
                return Response(
                    {'email': serializer.validated_data['email'], 'username': serializer.validated_data['username']}, 
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        if not username:
            return Response({'detail': 'Пожалуйста, предоставьте имя пользователя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь с таким username не найден.'},
                            status=status.HTTP_404_NOT_FOUND)
        if not confirmation_code:
            return Response({'detail': 'Пожалуйста, предоставьте confirmation code.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if user.confirmation_code != confirmation_code:
            return Response({'detail': 'Неверный confirmation code.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def get_current_user(self, request):
        if request.user.is_authenticated:
            if request.method == 'PATCH':
                serializer = self.get_serializer(
                    data=request.data, instance=request.user, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({'detail': 'Not authenticated.'}, status=status.HTTP_403_FORBIDDEN)

    def get_allowed_methods(self, detail=None):
        if self.action == 'get_current_user':
            return ['GET', 'PATCH', 'HEAD', 'OPTIONS']
        return super().get_allowed_methods(detail=detail)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrAdmin,)
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ('username', )
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        self.check_permissions(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial', False):
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
    def get_current_user(self, request):
        if request.method == 'DELETE':
            raise MethodNotAllowed('DELETE')
        if request.user.is_authenticated:
            if request.method == 'PATCH':
                serializer = self.get_serializer(
                    data=request.data, instance=request.user, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({'detail': 'Пользователь не авторизован.'}, status=status.HTTP_401_UNAUTHORIZED)
