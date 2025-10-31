from django.urls import path
from . import views

app_name = 'banner'

urlpatterns = [
    path('admin-pannel/banners/', views.BannerManagementView.as_view(), name='banner_management'),

]