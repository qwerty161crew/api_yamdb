from django.contrib import admin
from .models import Reviews, Titles, Categories
from import_export import resources
from import_export.admin import ImportExportModelAdmin

<<<<<<< HEAD
# класс обработки данных


class BookResource(resources.ModelResource):

    class Meta:
        model = Reviews

# вывод данных на странице


class BookAdmin(ImportExportModelAdmin):
    resource_classes = [BookResource]


admin.site.register(Reviews, BookAdmin)
=======
from reviews.models import User

admin.site.register(User)
>>>>>>> origin/feature/users
