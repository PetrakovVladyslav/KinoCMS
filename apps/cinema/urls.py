from django.urls import path
from . import views

app_name = 'cinema'

urlpatterns = [
    path('cinemas/', views.CinemaListView.as_view(), name='cinemas'),
    path('cinema/<slug:slug>/', views.CinemaDetailView.as_view(), name="cinema"),
    path('movies/', views.MovieListView.as_view(), name="movies"),
    path('movie/<slug:slug>/', views.MovieDetailView.as_view(), name='movie')

    ]
'''
urlpatterns = [
    path('cinemas/', views.CinemaListView.as_view(), name='cinemas'),
    ]
'''