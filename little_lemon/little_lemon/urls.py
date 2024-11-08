"""
URL configuration for little_lemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

import LittleLemonAPI.urls
from LittleLemonAPI.views import api_root

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_prometheus.urls")),
    re_path(r"^api/", include(LittleLemonAPI.urls)),
    re_path(r"", include("djoser.urls.authtoken")),
    re_path(r"^$", api_root, name="API-Root"),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]


if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
