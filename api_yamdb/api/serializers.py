from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Categorie, Title, Genre, Review, Comment
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator, EmailValidator
from reviews.models import Categorie, Title, Genre, Review, Comment, User

class ReviewsSerializers(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('title', 'text', 'author',  'score', 'pud_date' )
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

class CatigoriesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categorie


class TitlesSerializers(serializers.ModelSerializer):
    category = CatigoriesSerializers(many=False, read_only=True)
    genre = GenresSerializers(many=True, read_only=True)
    rating = serializers.FloatField(required=False)
    # rating = serializers.IntegerField(source='reviews__score__avg', read_only=True)
    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведений."""

    category = serializers.SlugRelatedField(
        queryset=Categorie.objects.all(), slug_field="slug"
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True
    )

    class Meta:
        fields = ("id", "name", "description", "year", "category", "genre")
        model = Title


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            # MaxLengthValidator(254),
            EmailValidator()
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            # MaxLengthValidator(150),
            RegexValidator(r'^[\w.@+-]+\Z'),
        ]
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('id', 'role')
    
    def validate_username(self, value):
        if value.lower() == 'me' or len(value) > 150:
            raise serializers.ValidationError('Использовать "me" запрещено, и длина имени не должны превышать 150 символов.')
        return value
    
    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError('Email не должен быть длиннее 254 символов.')
        return value
