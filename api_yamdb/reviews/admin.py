from django.contrib import admin

from .models import Categorie, Genre, Title, Review

admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Categorie)
admin.site.register(Review)
