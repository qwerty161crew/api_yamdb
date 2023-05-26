from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('categories', views.CategoriesViewSet, basename='catigories')
router.register('genres', views.GenresViewSet, basename='genre')
router.register('titles', views.TitlesViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewsViewSet,
    basename='review',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentsViewSet,
    basename='comment',
)
router.register('users', views.UserViewSet, basename='users')


app_name = 'api'

urlpatterns = [path('v1/', include((router.urls, 'api')))]
