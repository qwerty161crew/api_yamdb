from rest_framework import viewsets
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly, IsModerator
from django.shortcuts import get_object_or_404
from .serializers import ReviewsSerializers, TitlesSerializers, CommentsSerializers, CatigoriesSerializers, GenresSerializers
from .pagination import CustomPagination
from reviews.models import Review, Title, Comment, Categorie, Genre
from rest_framework.permissions import IsAuthenticatedOrReadOnly


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
    pagination_class = CustomPagination
