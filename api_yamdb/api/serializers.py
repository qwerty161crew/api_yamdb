from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.db import models
from rest_framework.generics import get_object_or_404

from reviews.models import Categorie, Title, Genre, Review, Comment


class ReviewsSerializers(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('__all__', )
        model = Review
        read_only_fields = ('id', 'author', 'pub_date')


class CommentsSerializers(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('__all__', )
        model = Comment
        read_only_fields = ('id', 'author', 'pub_date')


class GenresSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Genre
        read_only_fields = ('id', )


class TitlesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre')
        model = Title
        read_only_fields = ('id', )


class CatigoriesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Categorie
        read_only_fields = ('id', )
