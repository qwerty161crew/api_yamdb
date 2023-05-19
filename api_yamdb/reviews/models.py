from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


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
        Categorie, related_name='categories', on_delete=models.DO_NOTHING, null=True)
    genre = models.ManyToManyField(
        Genre, related_name='genre', blank=True)
    description = models.TextField(
        null=True, blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title, related_name='title', on_delete=models.CASCADE)
    text = models.CharField(max_length=10000)
    author = models.ForeignKey(
        User, related_name='author_reviews', on_delete=models.CASCADE)
    score = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        error_messages={'validators': 'Оценка от 1 до 10!'})
    pud_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, related_name='review', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    author = models.ForeignKey(
        User, related_name='author', on_delete=models.CASCADE)
    pud_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text