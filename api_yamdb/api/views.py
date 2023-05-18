from rest_framework import filters, mixins, viewsets, pagination, generics
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, IsAdminUser)
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnly, IsModerator, IsAdminOrReadOnly
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


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializers
    permission_classes = (IsAuthorOrReadOnly, IsModerator)
    pagination_class = CustomPagination
    

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        review=get_object_or_404(
                            Review, pk=self.kwargs.get('title_id')))


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CatigoriesSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CustomPagination


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = pagination.PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
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
            return Response({'message': 'Пользователь успешно создан!'}, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ('username', )
    lookup_field = 'username'

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
