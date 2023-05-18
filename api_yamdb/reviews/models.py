from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    ROLE_ANONYMOUS = 'anonymous'
    ROLE_AUTHENTICATED = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_ANONYMOUS, 'Аноним'),
        (ROLE_AUTHENTICATED, 'Аутентифицированный пользователь'),
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


class Categories(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    categories = models.ForeignKey(
        Categories, related_name='categories', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    titles = models.ManyToManyField(
        Titles, related_name='titles')

    def __str__(self):
        return self.titles


class Reviews(models.Model):
    title = models.ForeignKey(
        Titles, related_name='title', on_delete=models.CASCADE)
    text = models.CharField(max_length=10000)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='author_reviews', on_delete=models.CASCADE)
    score = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    pud_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Comments(models.Model):
    review = models.ForeignKey(
        Reviews, related_name='reviews', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='author', on_delete=models.CASCADE)
    pud_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
