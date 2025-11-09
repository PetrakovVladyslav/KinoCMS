from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_list, name='admin_users_list'),
    path('admin-panel/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('search/', views.search_movies, name='search_movies'),
]
