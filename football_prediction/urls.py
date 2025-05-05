"""
URL configuration for football_prediction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# from apps.users.views import CustomTokenCreateView

schema_view = get_schema_view(
    openapi.Info(
        title="User Management API",
        default_version="v1",
        description="API endpoints for Football Prediction",
        contact=openapi.Contact(email="tankoraphael@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("", RedirectView.as_view(url="api/v1/auth/redoc/", permanent=False)),
    path("superadmin/", admin.site.urls),
    # path("api/v1/auth/", include("djoser.urls")),
    # path("api/v1/auth/", include("djoser.urls.jwt")),
    path("api/v1/auth/", include("apps.users.urls.jwt", namespace="usersauth")),
    path("api/v1/auth/", include("apps.users.urls.base", namespace="usersapi")),
    path(
        "api/v1/auth/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/v1/auth/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(
        "api/v1/auth/swagger.json/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Football Prediction Admin"
admin.site.site_title = "Football Prediction Admin Portal"
admin.site.index_title = "Welcome to the Football Prediction Portal"
