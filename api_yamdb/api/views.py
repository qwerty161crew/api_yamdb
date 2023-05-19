from rest_framework import filters, mixins, viewsets, pagination, generics
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, IsAdminUser)
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnly, IsModerator, IsAdminOrReadOnly, IsSelfOrAdmin
from .pagination import CustomPagination

from reviews.models import Review, Title, Comment, Categorie, Genre, User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import ReviewsSerializers, TitlesSerializers, CommentsSerializers, CatigoriesSerializers, GenresSerializers, UserSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly, IsModerator)
    pagination_class = CustomPagination

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
        return title.reviews.all()


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CustomPagination
    search_fields = ('title_id', )

    # def perform_create(self, serializer):
    #     category_id = self.kwargs.get("category_id")
    #     category = get_object_or_404(Categorie, pk=category_id)
    #     serializer.save(category=category)
    #     return category.title.all()


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializers
    permission_classes = (IsAuthorOrReadOnly, IsModerator)
    pagination_class = CustomPagination

    def get_queryset(self):
        review = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        review=get_object_or_404(
                            Title, pk=self.kwargs.get('title_id')))


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
    def get_serializer_class(self):
        if self.request.method in ['POST']:
            return UserSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({'email': serializer.validated_data['email'], 'username': serializer.validated_data['username']}, status=status.HTTP_200_OK, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrAdmin,)
    search_fields = ('username', )
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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
