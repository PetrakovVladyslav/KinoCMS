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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard_demo(request):
    context = {
        'total_movies': 42,
        'total_sessions': 156, 
        'total_users': 1234,
        'total_pages': 8,
    }
    return render(request, 'core/admin_dashboard.html', context)

def home_view(request):
    return render(request, 'page/home.html')

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('admin-dashboard/', admin_dashboard_demo, name='admin_dashboard_demo'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('apps.core.urls')),
    path('', include('apps.cinema.urls')),
    path('', include('apps.users.urls'))
]




