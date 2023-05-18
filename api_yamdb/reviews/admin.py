from django.contrib import admin
from .models import User, Review
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# класс обработки данных


class BookResource(resources.ModelResource):

    class Meta:
        model = Review

# вывод данных на странице


class BookAdmin(ImportExportModelAdmin):
    resource_classes = [BookResource]


admin.site.register(Review, BookAdmin)
