from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.db import models
from rest_framework.generics import get_object_or_404

from reviews.models import Categories, Titles, Genres, Reviews, Comments


class ReviewsSerializers(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('__all__', )
        model = Reviews
        read_only_fields = ('id', 'author', 'pub_date')


class CommentsSerializers(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('__all__', )
        model = Comments
        read_only_fields = ('id', 'author', 'pub_date')


class GenresSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__', )
        model = Genres
        read_only_fields = ('id', )


class TitlesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__', )
        model = Titles
        read_only_fields = ('id', )


class CatigoriesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('__all__',)
        model = Categories
        read_only_fields = ('id', )
