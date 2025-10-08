from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView
from .models import Cinema, Movie, Hall

# Create your views here.

@login_required
def admin_dashboard(request):
    context = {
        'total_movies': 42,
        'total_sessions': 156, 
        'total_users': 1234,
        'total_pages': 8,
    }
    return render(request, 'core/admin_dashboard.html', context)

class CinemaListView(ListView):
    model = Cinema
    template_name = 'cinema/cinemas.html'
    context_object_name = 'cinemas'

class CinemaDetailView(DetailView):
    model = Cinema
    template_name = 'cinema/cinema.html'
    slug_field = 'slug'
    slug_url_kwarg = "slug"
    context_object_name = 'cinema'

class MovieListView(ListView):
    model = Movie
    template_name = 'cinema/movies.html'

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema/movie.html'