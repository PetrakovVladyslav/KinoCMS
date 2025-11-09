"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.i18n import set_language


@login_required
def admin_dashboard_demo(request):
    context = {
        "total_movies": 42,
        "total_sessions": 156,
        "total_users": 1234,
        "total_pages": 8,
    }
    return render(request, "core/admin_dashboard.html", context)


urlpatterns = [
    # path('', home_view, name='home'),  # Добавляем главную страницу в основные паттерны
    path("admin/", admin.site.urls),
    path("admin-dashboard/", admin_dashboard_demo, name="admin_dashboard_demo"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.banner.urls")),
    path("", include("apps.users.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("i18n/setlang/", set_language, name="set_language"),
]

# Добавляем поддержку интернационализации
urlpatterns += i18n_patterns(
    # path('', home_view, name='home_i18n')
    path("", include("apps.page.urls")),
    path("", include("apps.cinema.urls")),
)

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
