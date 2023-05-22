from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from api.views import MyTokenObtainPairView, SignUpViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc',
    ),
    path('api/v1/auth/signup/', SignUpViewSet.as_view(), name='signup'),
    path(
        'api/v1/auth/token/',
        MyTokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    path('api/', include('api.urls'), name='api'),
]
