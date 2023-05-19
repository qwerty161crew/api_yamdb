from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)
from rest_framework.routers import DefaultRouter

from . import views
router = DefaultRouter()

router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<reviews_id>\d+)',
                views.ReviewsViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<reviews_id>\d+)/comments/(?P<comment_id>\d+)',
                views.CommentsViewSet, basename='comments')


router.register('categories', views.CategoriesViewSet, basename='catigories')
router.register('genres', views.GenresViewSet, basename='genre')
router.register('titles', views.TitlesViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews', views.ReviewsViewSet, basename='review')
router.register('users', views.UserViewSet, basename='users')


app_name = 'api'

urlpatterns = [
    path('v1/', include((router.urls, 'api')))
]