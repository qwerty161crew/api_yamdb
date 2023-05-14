from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class Categories(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    pass


class Reviews(models.Model):
    pass


class Comments(models.Model):
    review = models.ForeignKey(Reviews, related_name='review')
    text = models.CharField()
    author = models.ForeignKey(User, related_name='author')
    pud_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Titles(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    categories = models.ForeignKey(Categories, related_name='categories')
