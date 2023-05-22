from rest_framework import serializers, exceptions
from rest_framework.relations import SlugRelatedField
from reviews.models import Categorie, Title, Genre, Review, Comment
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator, EmailValidator, MaxLengthValidator
from reviews.models import Categorie, Title, Genre, Review, Comment, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.cache import cache
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.state import api_settings
from rest_framework import status

class ReviewsSerializers(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        if Review.objects.filter(
            author=self.context['request'].user,
            title__id=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise serializers.ValidationError(
                'Отзыв можно оставить единожды'
            )
        return data


class CommentsSerializers(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
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
    rating = serializers.FloatField(required=False)
    
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


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        if not username:
            raise exceptions.ValidationError({'username': 'Пожалуйста, предоставьте имя пользователя.'})
        if not confirmation_code:
            return Response({'detail': 'Пожалуйста, предоставьте confirmation code.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator()
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(r'^[\w.@+-]+\Z'),
        ]
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'bio', 'first_name', 'last_name')
        read_only_fields = ('id',)
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('id')
        return ret
    
    def update(self, instance, validated_data):
        if 'role' in validated_data and self.context['request'].path == '/api/v1/users/me/':
            validated_data.pop('role')
        return super().update(instance, validated_data)
    
    def validate_username(self, value):
        if value.lower() == 'me' or len(value) > 150:
            raise serializers.ValidationError('Использовать "me" запрещено, и длина имени не должны превышать 150 символов.')
        return value
    
    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError('Email не должен быть длиннее 254 символов.')
        return value