from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)
from rest_framework.routers import SimpleRouter

from . import views
router = SimpleRouter()

router.register(r'/titles/(?P<title_id>\d+)/reviews/(?P<reviews_id>\d+)',
                views.ReviewsViewSet, basename='reviews')
router.register(r'/categories/(?P<slug>\d+)',
                views.CategoriesViewSet, basename='categories')
router.register(r'/titles/(?P<title_id>\d+)',
                views.TitlesViewSet, basename='titles')
router.register(r'/titles/(?P<title_id>\d+)/reviews/(?P<reviews_id>\d+)/comments/(?P<comment_id>\d+)',
                views.CommentsViewSet, basename='comments')
router.register(r'/genres/(?P<slug>\d+)',
                views.GenresViewSet, basename='genres')

app_name = 'api'

urlpatterns = [
    path('v1/', include((router.urls, 'api')))
]
