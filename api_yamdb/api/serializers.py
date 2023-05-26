from typing import Any, Dict

from django.core.validators import (
    EmailValidator,
    MaxLengthValidator,
    RegexValidator,
)
from rest_framework import exceptions, serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Categorie, Comment, Genre, Review, Title, User


class ReviewsSerializers(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(
        self: 'ReviewsSerializers',
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        if self.context['request'].method != 'POST':
            return data
        if Review.objects.filter(
            author=self.context['request'].user,
            title__id=self.context['view'].kwargs.get('title_id'),
        ).exists():
            raise serializers.ValidationError('Отзыв можно оставить единожды')
        return data


class CommentsSerializers(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class GenresSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CatigoriesSerializers(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categorie


class TitlesSerializers(serializers.ModelSerializer):
    category = CatigoriesSerializers(many=False, read_only=True)
    genre = GenresSerializers(many=True, read_only=True)
    rating = serializers.IntegerField(source='reviews__score__avg',
                                      read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
            'rating',
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Categorie.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        fields = ('id', 'name', 'description', 'year', 'category', 'genre')
        model = Title


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(
        self: 'MyTokenObtainPairSerializer',
        attrs: Dict[str, Any],
    ) -> Dict[str, Any]:
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        if not username:
            raise exceptions.ValidationError(
                {'username': 'Пожалуйста, предоставьте имя пользователя.'},
            )
        if not confirmation_code:
            return Response(
                {'detail': 'Пожалуйста, предоставьте confirmation code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator(),
            MaxLengthValidator(254),
        ],
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(r'^[\w.@+-]+\Z'),
            MaxLengthValidator(150),
        ],
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'role',
            'bio',
            'first_name',
            'last_name',
        )

    def update(
        self: 'UserSerializer',
        instance: User,
        validated_data: Dict[str, Any],
    ) -> User:
        if 'role' in validated_data and self.context.get('change_self'):
            validated_data.pop('role')
        return super().update(instance, validated_data)

    def validate_username(self: 'UserSerializer', value: str) -> str:
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено.',
            )
        return value
