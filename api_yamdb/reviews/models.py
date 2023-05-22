from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint
import secrets


class User(AbstractUser):
    ROLE_ANONYMOUS = 'anonymous'
    ROLE_AUTHENTICATED = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_ANONYMOUS, 'Аноним'),
        (ROLE_AUTHENTICATED,
         'Аутентифицированный пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Администратор'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_AUTHENTICATED,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    confirmation_code = models.CharField(max_length=12, null=True, blank=True)

    def generate_confirmation_code(self):
        self.confirmation_code = secrets.token_hex(6)
        self.save()

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
        super().save(*args, **kwargs)



class Categorie(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField(
    )
    category = models.ForeignKey(
        Categorie, related_name='categories', on_delete=models.DO_NOTHING, null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, related_name='genre', blank=True)
    description = models.TextField(
        null=True, blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    def rating(self):
        scores = self.reviews.values_list('score', flat=True)
        if len(scores) != 0:
            return sum(scores) / len(scores)
        return None


class Review(models.Model):
    text = models.TextField()
    title = models.ForeignKey(
        Title, related_name='reviews', on_delete=models.CASCADE)
    text = models.CharField(max_length=10000)
    author = models.ForeignKey(
        User, related_name='author_reviews', on_delete=models.CASCADE)
    score = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        error_messages={'validators': 'Оценка от 1 до 10!'})
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, related_name='comment', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    author = models.ForeignKey(
        User, related_name='author', on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tex
