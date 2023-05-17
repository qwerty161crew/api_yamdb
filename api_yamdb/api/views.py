from rest_framework import filters, mixins, viewsets, pagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, IsAdminUser)
from django.shortcuts import get_object_or_404
from .permissions import IsAdminOrReadOnly

from .serializers import ReviewsSerializers, TitlesSerializers, CommentsSerializers, CatigoriesSerializers, GenresSerializers
from .pagination import CustomPagination
from reviews.models import Review, Title, Comment, Categorie, Genre


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewsSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentsSerializers
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CatigoriesSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CustomPagination


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializers
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CustomPagination
