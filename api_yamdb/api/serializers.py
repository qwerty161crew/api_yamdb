from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.db import models
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from reviews.models import Categorie, Title, Genre, Review, Comment
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator, EmailValidator, MaxLengthValidator

from reviews.models import Categorie, Title, Genre, Review, Comment, User

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
        fields = ('name', 'slug')
        model = Genre
        # read_only_fields = ('id', )


class TitlesSerializers(serializers.ModelSerializer):
    # category = SlugRelatedField(slug_field='category_id', read_only=True)
    # genre = SlugRelatedField(slug_field='genre_id', read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre', 'description')
        model = Title
        read_only_fields = ('id', )


class CatigoriesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Categorie
        read_only_fields = ('id', )


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(254),
            EmailValidator()
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(150),
            RegexValidator(r'^[\w.@+-]+\Z'),
        ]
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'bio', 'first_name', 'last_name')
    
    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Использовать имя "me" в качестве username запрещено.')
        return value
