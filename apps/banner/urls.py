from django.urls import path
from . import views

app_name = 'banner'

urlpatterns = [
    path('admin-panel/banners/', views.BannerManagementView.as_view(), name='banner_management'),
]
