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
    
    # Halls
    path('admin-panel/cinemas/<int:cinema_id>/halls/create/', views.hall_create_view, name='admin_hall_create'),
    path('admin-panel/halls/<int:pk>/edit/', views.hall_update_view, name='admin_hall_edit'),
    path('admin-panel/halls/<int:pk>/delete/', views.hall_delete_view, name='admin_hall_delete'),
    
    # Public pages
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('cinemas/', views.cinema_view, name='cinema_list'),
    path('cinema/<int:pk>/', views.CinemaDetailView.as_view(), name='cinema_detail'),
    path('hall/<int:pk>/', views.HallDetailView.as_view(), name='hall_detail'),
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('booking/<int:pk>/', views.BookingView.as_view(), name='booking'),
    
    # API endpoints
    path('api/booking/<int:session_id>/process/', views.process_booking, name='process_booking'),
]

