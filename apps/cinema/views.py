from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.contrib import messages
from datetime import date

from .models import Cinema, Movie, Hall
from .forms import PageMovieForm, CinemaForm
from apps.core.models import Gallery, SeoBlock
from apps.core.forms import SeoBlockForm, GalleryFormSet

# Create your views here.


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema/movie.html'
    context_object_name = 'movie'


class CinemaDetailView(DetailView):
    model = Cinema
    template_name = 'cinema/cinema_detail.html'
    context_object_name = 'cinema'


@staff_member_required(login_url='admin:login')
def admin_movie_list_view(request):
    today = date.today()

    current_movies = Movie.objects.filter(start_date__lte=today, end_date__gte=today)
    upcoming_movies = Movie.objects.filter(start_date__gt=today)

    context = {
        'today': today,
        'current_movies': current_movies,
        'upcoming_movies': upcoming_movies,

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
    # Placeholder - redirect back to cinema edit
    messages.info(request, 'Функция создания зала будет реализована позже')
    return redirect('cinema:cinema_edit', pk=cinema_id)


@staff_member_required(login_url='admin:login')
def hall_update_view(request, pk):
    hall = get_object_or_404(Hall, pk=pk)
    # Placeholder - redirect back to cinema edit
    messages.info(request, 'Функция редактирования зала будет реализована позже')
    return redirect('cinema:cinema_edit', pk=hall.cinema.pk)


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

