from django.urls import path
from . import views

app_name = 'cinema'

urlpatterns = [
    path('admin-panel/movies/', views.admin_movie_list_view, name='admin_movie_list'),
    path('admin-panel/movies/create/', views.movie_create_view, name='movie_create'),
    path('admin-panel/movies/<int:movie_id>/edit/', views.movie_update_view, name='movie_edit'),
    path('admin-panel/movies/<int:movie_id>/delete/', views.movie_delete_view, name='movie_delete'),
    
    # Public movie detail page
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),

]
'''
urlpatterns = [
    path('cinemas/', views.CinemaListView.as_view(), name='cinemas'),
    ]
'''