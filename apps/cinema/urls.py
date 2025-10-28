from django.urls import path
from . import views

app_name = 'cinema'

urlpatterns = [
    path('admin-panel/movies/', views.admin_movie_list_view, name='admin_movie_list'),
    path('admin-panel/movies/create/', views.movie_create_view, name='movie_create'),
    path('admin-panel/movies/<int:movie_id>/edit/', views.movie_update_view, name='movie_edit'),
    path('admin-panel/movies/<int:movie_id>/delete/', views.movie_delete_view, name='movie_delete'),


    path('admin-panel/cinemas/create/', views.cinema_create_view, name='cinema_create'),
    path('admin-panel/cinemas/', views.admin_cinema_list_view, name='admin_cinema_list'),
    path('admin-panel/cinemas/<int:pk>/edit/', views.cinema_update_view, name='cinema_edit'),
    path('admin-panel/cinemas/<int:pk>/delete/', views.cinema_delete_view, name='cinema_delete'),
    
    # Public pages
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('cinemas/', views.cinema_view, name='cinema_list'),

]
