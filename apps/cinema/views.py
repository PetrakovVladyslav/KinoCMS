from dateutil.utils import today
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView, CreateView
from more_itertools.recipes import totient
from django.contrib import messages
from .forms import PageMovieForm

from .models import Cinema, Movie, Hall
from datetime import date
from .models import Movie, Gallery
from apps.core.models import Gallery, SeoBlock

# Create your views here.


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema/movie.html'
    context_object_name = 'movie'

@login_required
def admin_dashboard(request):
    context = {
        'total_movies': 42,
        'total_sessions': 156,
        'total_users': 1234,
        'total_pages': 8,
    }
    return render(request, 'core/admin_dashboard.html', context)


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
            movie.can_delete = True

            seo_block = None
            if seo_form.has_changed():
                seo_block = seo_form.save()
                movie.seo_block = seo_block

            movie.save()

            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if not f.cleaned_data.get('DELETE', False))
            if has_images:
                gallery = Gallery.objects.create(name=f'Галерея - {movie.title or movie.pk}')
                movie.gallery = gallery
                movie.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Фильм "{movie.title}" успешно создан')
            return redirect('cinema:admin_movie_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
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
        movie_title = movie.title_ru or movie.title

        if movie.gallery:
            movie.gallery.images.all().delete()
            movie.gallery.delete()

        if movie.seo_block:
            movie.seo_block.delete()

        movie.delete()

        messages.success(request, f'Фильм "{movie_title}" и все связанные данные успешно удалены')
        return redirect('cinema:admin_movie_list')

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
            movie.save()

            if seo_form.has_changed():
                seo_block = seo_form.save(commit=False)
                seo_block.save()
                movie.seo_block = seo_block
                movie.save()

            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if not f.cleaned_data.get('DELETE', False))
            if has_images and not movie.gallery_id:
                gallery = Gallery.objects.create(name=f'Галерея - {movie.title or movie.pk}')
                movie.gallery = gallery
                movie.save()
                gallery_formset.instance = gallery

            gallery_formset.save()

            messages.success(request, f'Фильм "{movie.title}" успешно обновлён')
            return redirect('cinema:admin_movie_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')

    else:
        form = PageMovieForm(instance=movie)
        seo_form = SeoBlockForm(instance=movie.seo_block if movie.seo_block_id else None)
        gallery_formset = GalleryFormSet(instance=movie.gallery if movie.gallery_id else None)

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'movie': movie,
        'title': f'Редактировать фильм "{movie.title}"',
        'is_create': False,
    }
    return render(request, 'cinema/admin_movie_form.html', context)


@staff_member_required(login_url='admin:login')
def cinema_create_view(request):

    if request.method == 'POST':
        form = CinemaForm(request.POST, request.FILES)
        seo_form = SeoBlockForm1(request.POST)
        image_formset = GalleryGalleryFormSet(request.POST, request.FILES, queryset=Gallery.objects.none())

        if form.is_valid() and seo_form.is_valid() and image_formset.is_valid():
            cinema = form.save(commit=False)
        if seo_form.has_changed():
            seo_block1= seo_form.save()
            cinema.seo_block1 = seo_block1

        cinema.save()
        form.save_m2m()

        images = image_formset.save(commit=False)
        for image in images:
            image.save()
            cinema.gallery1.add(image)

        for image in image_formset.deleted_objects:
            image.delete()

        messages.success(request,'Кинотеатр создан')
        return redirect('cinema:admin_cinema_list')

    else:
        form = CinemaForm()
        seo_form = SeoBlockForm1()
        image_formset = GalleryGalleryFormSet(queryset=Gallery.objects.none())

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': image_formset,
        'title': 'Создать новый кинотеатр',
        'is_create': True,
    }
    return render(request, 'cinema/admin_cinema_form.html', context)


@staff_member_required(login_url='admin:login')
def cinema_update_view(request, pk):
    cinema = get_object_or_404(Cinema, pk=pk)

    if request.method == 'POST':
        form = CinemaForm(request.POST, request.FILES, instance=cinema)

        seo_form = SeoBlockForm1(request.POST, instance=cinema.seo_block1 if cinema.seo_block1_id else None)

        image_formset = GalleryGalleryFormSet(request.POST, request.FILES, queryset=cinema.gallery1.all())


        if form.is_valid() and seo_form.is_valid() and image_formset.is_valid():
            cinema = form.save(commit=False)

            if seo_form.has_changed():
                seo_block1 = seo_form.save()
                cinema.seo_block1 = seo_block1

            cinema.save()
            form.save_m2m()

            images = image_formset.save(commit=False)
            for image in images:
                image.save()
                cinema.gallery1.add(image)

            for image in image_formset.deleted_objects:
                cinema.gallery1.remove(image)
                image.delete()

            messages.success(request, f'Кинотеатр "{cinema.name}" успешно обновлён.')
            return redirect('cinema:admin_cinema_list')

    else:
        form = CinemaForm(instance=cinema)
        seo_form = SeoBlockForm1(instance=cinema.seo_block1 if cinema.seo_block1 else None)
        image_formset = GalleryGalleryFormSet(queryset=cinema.gallery1.all())

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': image_formset,
        'cinema': cinema,
        'title': f'Редактировать кинотеатр "{cinema.name}"',
        'is_create': False,
    }

    return render(request, 'cinema/admin_cinema_form.html', context)

@staff_member_required(login_url='admin:login')
def cinema_delete_view(request, pk):
    cinema = get_object_or_404(Cinema, pk=pk)

    if request.method == 'POST':
        for image in cinema.gallery1.all():
            image.delete()

        if cinema.seo_block1:
            cinema.seo_block1.delete()

        cinema.delete()

        messages.success(request, f'Кинотеатр "{cinema.name}" и все связанные данные успешно удалены')
        return redirect('cinema:admin_cinema_list')

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
        'title': 'Список киноетатров '

    }

    return render(request, 'cinema/cinema_list.html', context)


class CinemaDetailView(DetailView):
    model = Cinema
    template_name = 'cinema/cinema.html'
    context_object_name = 'cinema'
