from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.contrib import messages
from datetime import date, timedelta
from itertools import groupby

from .models import Cinema, Movie, Hall, Session
from .forms import PageMovieForm, CinemaForm, HallForm
from .enums import MovieFormat
from apps.core.models import Gallery, SeoBlock
from apps.core.forms import SeoBlockForm, GalleryFormSet

# Create your views here.


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema/movie.html'
    context_object_name = 'movie'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        
        # Get sessions for this movie (today and tomorrow)
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        sessions = Session.objects.filter(
            movie=movie,
            start_time__date__in=[today, tomorrow]
        ).select_related('hall', 'hall__cinema').order_by('start_time')
        
        # Get unique cinemas that have sessions for this movie
        cinemas = Cinema.objects.filter(
            halls__session__movie=movie,
            halls__session__start_time__date__in=[today, tomorrow]
        ).distinct()
        
        # Group sessions by date
        sessions_by_date = {}
        for session_date, group in groupby(sessions, key=lambda s: s.start_time.date()):
            sessions_by_date[session_date] = list(group)
        
        # Group sessions by cinema
        from collections import defaultdict
        sessions_by_cinema = defaultdict(list)
        for session in sessions:
            sessions_by_cinema[session.hall.cinema.id].append(session)
        
        # Convert to list of tuples (cinema, sessions_list)
        cinema_sessions = []
        for cinema in cinemas:
            if cinema.id in sessions_by_cinema:
                cinema_sessions.append((cinema, sessions_by_cinema[cinema.id]))
        
        context['sessions'] = sessions
        context['cinemas'] = cinemas
        context['sessions_by_date'] = sessions_by_date
        context['cinema_sessions'] = cinema_sessions
        context['today'] = today
        context['tomorrow'] = tomorrow
        
        return context


class CinemaDetailView(DetailView):
    model = Cinema
    template_name = 'cinema/cinema.html'
    context_object_name = 'cinema'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cinema = self.get_object()
        
        # Get today's sessions for all halls in this cinema
        today = date.today()
        today_sessions = Session.objects.filter(
            hall__cinema=cinema,
            start_time__date=today
        ).select_related('movie', 'hall').order_by('start_time')
        
        context['today_sessions'] = today_sessions
        return context


class HallDetailView(DetailView):
    model = Hall
    template_name = 'cinema/hall.html'
    context_object_name = 'hall'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hall = self.get_object()
        
        # Get today's sessions for this hall
        from datetime import date
        today = date.today()
        today_sessions = hall.session_set.filter(
            start_time__date=today
        ).select_related('movie').order_by('start_time')
        
        context['today_sessions'] = today_sessions
        return context


@staff_member_required(login_url='admin:login')
def admin_movie_list_view(request):
    today = date.today()

    current_movies = Movie.objects.filter(start_date__lte=today, end_date__gte=today)
    upcoming_movies = Movie.objects.filter(start_date__gt=today)
    past_movies = Movie.objects.filter(end_date__lt=today)
    movies_without_dates = Movie.objects.filter(start_date__isnull=True) | Movie.objects.filter(end_date__isnull=True)

    context = {
        'today': today,
        'current_movies': current_movies,
        'upcoming_movies': upcoming_movies,
        'past_movies': past_movies,
        'movies_without_dates': movies_without_dates,

    }

    return render(request, 'cinema/admin_movie_list.html', context)

@staff_member_required(login_url='admin:login')
def movie_create_view(request):
    if request.method == 'POST':
        form = PageMovieForm(request.POST, request.FILES)
        seo_form = SeoBlockForm(request.POST)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)

        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            movie = form.save(commit=False)

            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                movie.seo_block = seo_block

            movie.save()

            # Галерея
            has_images = any(
                bool(f.cleaned_data.get('image'))
                for f in gallery_formset.forms
                if not f.cleaned_data.get('DELETE', False)
            )

            if has_images:
                gallery = Gallery.objects.create(
                    name=f'Галерея - {movie.name}'
                )
                movie.gallery = gallery
                movie.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Фильм "{movie.name}" создан')
            return redirect('cinema:admin_movie_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageMovieForm()
        seo_form = SeoBlockForm()
        gallery_formset = GalleryFormSet()

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'title': 'Создать новый фильм',
        'is_create': True,
    }
    return render(request, 'cinema/admin_movie_form.html', context)

@staff_member_required(login_url='admin:login')
def movie_delete_view(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        movie_name = movie.name

        if movie.gallery:
            movie.gallery.images.all().delete()
            movie.gallery.delete()

        if movie.seo_block:
            movie.seo_block.delete()

        movie.delete()
        messages.success(request, f'Фильм "{movie_name}" успешно удален')
        return redirect('cinema:admin_movie_list')
    else:
        messages.warning(request, 'Некорректная попытка удаления')
        return redirect('cinema:admin_movie_list')

@staff_member_required(login_url='admin:login')
def movie_update_view(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        form = PageMovieForm(request.POST, request.FILES, instance=movie)
        seo_form = SeoBlockForm(request.POST, instance=movie.seo_block if movie.seo_block_id else None)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=movie.gallery if movie.gallery_id else None)

        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            movie = form.save(commit=False)

            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                movie.seo_block = seo_block

            # Галерея - создаем, если нужно
            has_images = any(
                bool(f.cleaned_data.get('image'))
                for f in gallery_formset.forms
                if not f.cleaned_data.get('DELETE', False)
            )

            if has_images and not movie.gallery:
                gallery = Gallery.objects.create(
                    name=f'Галерея - {movie.name}'
                )
                movie.gallery = gallery
                gallery_formset.instance = gallery

            movie.save()

            # Галерея
            if movie.gallery:
                gallery_formset.save()

            messages.success(request, f'Фильм "{movie.name}" обновлен')
            return redirect('cinema:admin_movie_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageMovieForm(instance=movie)
        seo_form = SeoBlockForm(instance=movie.seo_block if movie.seo_block_id else None)
        gallery_formset = GalleryFormSet(instance=movie.gallery if movie.gallery_id else None)

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'movie': movie,
        'title': f'Редактировать фильм "{movie.name}"',
        'is_create': False,
    }
    return render(request, 'cinema/admin_movie_form.html', context)


@staff_member_required(login_url='admin:login')
def cinema_create_view(request):
    if request.method == 'POST':
        form = CinemaForm(request.POST, request.FILES)
        seo_form = SeoBlockForm(request.POST)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)

        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            cinema = form.save(commit=False)

            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                cinema.seo_block = seo_block

            cinema.save()

            # Галерея
            has_images = any(
                bool(f.cleaned_data.get('image'))
                for f in gallery_formset.forms
                if not f.cleaned_data.get('DELETE', False)
            )

            if has_images:
                gallery = Gallery.objects.create(
                    name=f'Галерея - {cinema.name}'
                )
                cinema.gallery = gallery
                cinema.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Кинотеатр "{cinema.name}" создан')
            return redirect('cinema:admin_cinema_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = CinemaForm()
        seo_form = SeoBlockForm()
        gallery_formset = GalleryFormSet()

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'title': 'Создать новый кинотеатр',
        'is_create': True,
    }
    return render(request, 'cinema/admin_cinema_form.html', context)


@staff_member_required(login_url='admin:login')
def cinema_update_view(request, pk):
    cinema = get_object_or_404(Cinema, pk=pk)

    if request.method == 'POST':
        form = CinemaForm(request.POST, request.FILES, instance=cinema)
        seo_form = SeoBlockForm(request.POST, instance=cinema.seo_block if cinema.seo_block_id else None)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=cinema.gallery if cinema.gallery_id else None)

        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            cinema = form.save(commit=False)

            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                cinema.seo_block = seo_block

            # Галерея - создаем, если нужно
            has_images = any(
                bool(f.cleaned_data.get('image'))
                for f in gallery_formset.forms
                if not f.cleaned_data.get('DELETE', False)
            )

            if has_images and not cinema.gallery:
                gallery = Gallery.objects.create(
                    name=f'Галерея - {cinema.name}'
                )
                cinema.gallery = gallery
                gallery_formset.instance = gallery

            cinema.save()

            # Галерея
            if cinema.gallery:
                gallery_formset.save()

            messages.success(request, f'Кинотеатр "{cinema.name}" обновлен')
            return redirect('cinema:admin_cinema_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = CinemaForm(instance=cinema)
        seo_form = SeoBlockForm(instance=cinema.seo_block if cinema.seo_block_id else None)
        gallery_formset = GalleryFormSet(instance=cinema.gallery if cinema.gallery_id else None)

    halls = cinema.halls.all().order_by('created_at')
    
    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'cinema': cinema,
        'halls': halls,
        'title': f'Редактировать кинотеатр "{cinema.name}"',
        'is_create': False,
    }
    return render(request, 'cinema/admin_cinema_form.html', context)

@staff_member_required(login_url='admin:login')
def cinema_delete_view(request, pk):
    cinema = get_object_or_404(Cinema, pk=pk)

    if request.method == 'POST':
        cinema_name = cinema.name

        if cinema.gallery:
            cinema.gallery.images.all().delete()
            cinema.gallery.delete()

        if cinema.seo_block:
            cinema.seo_block.delete()

        cinema.delete()
        messages.success(request, f'Кинотеатр "{cinema_name}" успешно удален')
        return redirect('cinema:admin_cinema_list')
    else:
        messages.warning(request, 'Некорректная попытка удаления')
        return redirect('cinema:admin_cinema_list')

@staff_member_required(login_url='admin:login')
def admin_cinema_list_view(request):

    cinemas = Cinema.objects.all().order_by('-id')

    context = {
        'cinemas': cinemas,
        'title': 'Список киноетатров '

    }

    return render(request, 'cinema/admin_cinema_list.html', context)


def cinema_view(request):

    cinemas = Cinema.objects.all().order_by('-id')

    context = {
        'cinemas': cinemas,
        'title': 'Список кинотеатров '

    }

    return render(request, 'cinema/cinema_list.html', context)


@staff_member_required(login_url='admin:login')
def hall_create_view(request, cinema_id):
    cinema = get_object_or_404(Cinema, pk=cinema_id)
    
    if request.method == 'POST':
        form = HallForm(request.POST, request.FILES)
        seo_form = SeoBlockForm(request.POST)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)
        
        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            hall = form.save(commit=False)
            hall.cinema = cinema
            
            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                hall.seo_block = seo_block
            
            hall.save()
            
            # Галерея
            has_images = any(
                bool(f.cleaned_data.get('image'))
                for f in gallery_formset.forms
                if not f.cleaned_data.get('DELETE', False)
            )
            
            if has_images:
                gallery = Gallery.objects.create(
                    name=f'Галерея - {hall.name}'
                )
                hall.gallery = gallery
                hall.save()
                gallery_formset.instance = gallery
                gallery_formset.save()
            
            messages.success(request, f'Зал "{hall.name}" создан')
            return redirect('cinema:cinema_edit', pk=cinema_id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = HallForm()
        seo_form = SeoBlockForm()
        gallery_formset = GalleryFormSet()
    
    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'cinema': cinema,
        'title': f'Создать зал для {cinema.name}',
        'is_create': True,
    }
    return render(request, 'cinema/admin_hall_form.html', context)


@staff_member_required(login_url='admin:login')
def hall_update_view(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    cinema = hall.cinema
    
    if request.method == 'POST':
        form = HallForm(request.POST, request.FILES, instance=hall)
        seo_form = SeoBlockForm(request.POST, instance=hall.seo_block if hall.seo_block_id else None)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=hall.gallery if hall.gallery_id else None)
        
        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            hall = form.save(commit=False)
            
            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                hall.seo_block = seo_block
            
            # Галерея - создаем, если нужно
            has_images = any(
                bool(f.cleaned_data.get('image'))
                for f in gallery_formset.forms
                if not f.cleaned_data.get('DELETE', False)
            )
            
            if has_images and not hall.gallery:
                gallery = Gallery.objects.create(
                    name=f'Галерея - {hall.name}'
                )
                hall.gallery = gallery
                gallery_formset.instance = gallery
            
            hall.save()
            
            # Галерея
            if hall.gallery:
                gallery_formset.save()
            
            messages.success(request, f'Зал "{hall.name}" обновлен')
            return redirect('cinema:cinema_edit', pk=cinema.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = HallForm(instance=hall)
        seo_form = SeoBlockForm(instance=hall.seo_block if hall.seo_block_id else None)
        gallery_formset = GalleryFormSet(instance=hall.gallery if hall.gallery_id else None)
    
    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'cinema': cinema,
        'hall': hall,
        'title': f'Редактировать зал "{hall.name}"',
        'is_create': False,
    }
    return render(request, 'cinema/admin_hall_form.html', context)

@staff_member_required(login_url='admin:login')
def hall_delete_view(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    cinema_id = hall.cinema.pk
    
    if request.method == 'POST':
        hall_name = hall.name
        
        if hall.gallery:
            hall.gallery.images.all().delete()
            hall.gallery.delete()
        
        if hall.seo_block:
            hall.seo_block.delete()
        
        hall.delete()
        messages.success(request, f'Зал "{hall_name}" успешно удален')
    else:
        messages.warning(request, 'Некорректная попытка удаления')
    
    return redirect('cinema:cinema_edit', pk=cinema_id)


class SessionListView(ListView):
    model = Session
    template_name = 'cinema/session.html'
    context_object_name = 'sessions'
    
    def get_queryset(self):
        queryset = Session.objects.select_related(
            'movie', 'hall', 'hall__cinema'
        ).order_by('start_time')
        
        # Filter by format (multiple selection)
        format_filters = self.request.GET.getlist('format')
        if format_filters:
            queryset = queryset.filter(format__in=format_filters)
        
        # Filter by cinema
        cinema_id = self.request.GET.get('cinema')
        if cinema_id:
            queryset = queryset.filter(hall__cinema_id=cinema_id)
        
        # Filter by date
        date_filter = self.request.GET.get('date')
        if date_filter:
            queryset = queryset.filter(start_time__date=date_filter)
        
        # Filter by movie
        movie_id = self.request.GET.get('movie')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        
        # Filter by hall
        hall_id = self.request.GET.get('hall')
        if hall_id:
            queryset = queryset.filter(hall_id=hall_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter choices
        context['formats'] = MovieFormat.choices
        context['cinemas'] = Cinema.objects.all()
        context['movies'] = Movie.objects.filter(
            start_date__lte=date.today()
        ).order_by('name')
        context['halls'] = Hall.objects.select_related('cinema').all()
        
        # Preserve current filters
        context['current_formats'] = self.request.GET.getlist('format')
        context['current_cinema'] = self.request.GET.get('cinema', '')
        context['current_date'] = self.request.GET.get('date', '')
        context['current_movie'] = self.request.GET.get('movie', '')
        context['current_hall'] = self.request.GET.get('hall', '')
        
        # Group sessions by date
        sessions = context['sessions']
        sessions_by_date = {}
        for session_date, group in groupby(sessions, key=lambda s: s.start_time.date()):
            sessions_by_date[session_date] = list(group)
        
        context['sessions_by_date'] = sessions_by_date
        
        # Add today and tomorrow for booking validation
        today = date.today()
        context['today'] = today
        context['tomorrow'] = today + timedelta(days=1)
        
        return context

