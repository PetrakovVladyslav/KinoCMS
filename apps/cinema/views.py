from dateutil.utils import today
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView, CreateView
from more_itertools.recipes import totient
from django.contrib import messages
from .forms import ImageFormSet, CinemaForm, GalleryImageFormSet
from .forms import PageMovieForm, SeoBlockForm1, SeoBlockForm

from .models import Cinema, Movie, Hall
from datetime import date
from .models import Movie, Image1
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
        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=None)

        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            # 1) Сначала готовим movie (commit=False — чтобы можно было привязать seo/gallery после)
            movie = form.save(commit=False)
            movie.can_delete = True
            # ещё не сохраняем movie, т.к. хотим сначала создать seo и/или галерею при необходимости

            # 2) Создаём SEO-блок только если в форме есть данные (has_changed())
            seo_block = None
            if seo_form.has_changed():
                seo_block = seo_form.save()
                movie.seo_block = seo_block

            # 3) Сохраняем movie, чтобы получить PK
            movie.save()

            # 4) Если есть изображения в formset — создаём галерею и сохраняем formset
            # Проверка: есть ли хотя бы одна заполненная форма изображения
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
        gallery_formset = ImageFormSet()

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

        # Удаляем связанные объекты
        if movie.gallery:
            # Удаляем все изображения из галереи
            movie.gallery.images.all().delete()
            # Удаляем саму галерею
            movie.gallery.delete()

        if movie.seo_block:
            movie.seo_block.delete()

        # Удаляем фильм (сеансы удалятся автоматически через каскад)
        movie.delete()

        messages.success(request, f'Фильм "{movie_title}" и все связанные данные успешно удалены')
        return redirect('cinema:admin_movie_list')

    # Если не POST запрос, перенаправляем обратно
    return redirect('cinema:admin_movie_list')

@staff_member_required(login_url='admin:login')
def movie_update_view(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    # В GET не создаём seo/gallery автоматически — только если их нет и пользователь сохранит новые данные
    if request.method == 'POST':
        form = PageMovieForm(request.POST, request.FILES, instance=movie)

        # Передаём instance в seo_form только если seo_block действительно существует
        seo_form = SeoBlockForm(request.POST, instance=movie.seo_block if movie.seo_block_id else None)

        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=movie.gallery if movie.gallery_id else None)

        if form.is_valid() and seo_form.is_valid() and gallery_formset.is_valid():
            # Сохраняем movie
            movie = form.save(commit=False)
            movie.save()

            # SEO: если форма содержит изменения — сохраняем и привязываем
            if seo_form.has_changed():
                seo_block = seo_form.save(commit=False)
                # если у seo_block есть required FK к movie, установить связь здесь; иначе — просто сохранить
                seo_block.save()
                movie.seo_block = seo_block
                movie.save()

            # Gallery: если есть загруженные изображения и галерея ещё не создана — создаём
            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if not f.cleaned_data.get('DELETE', False))
            if has_images and not movie.gallery_id:
                gallery = Gallery.objects.create(name=f'Галерея - {movie.title or movie.pk}')
                movie.gallery = gallery
                movie.save()
                gallery_formset.instance = gallery

            # Сохраняем formset (если instance определён)
            gallery_formset.save()

            messages.success(request, f'Фильм "{movie.title}" успешно обновлён')
            return redirect('cinema:admin_movie_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')

    else:
        # GET: инициализация форм — не создаём новые объекты, только используем существующие
        form = PageMovieForm(instance=movie)
        seo_form = SeoBlockForm(instance=movie.seo_block if movie.seo_block_id else None)
        gallery_formset = ImageFormSet(instance=movie.gallery if movie.gallery_id else None)

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': gallery_formset,
        'movie': movie,
        'title': f'Редактировать фильм "{movie.title}"',
        'is_create': False,
    }
    return render(request, 'cinema/admin_movie_form.html', context)



def cinema_create_view(request):

    if request.method == 'POST':
        form = CinemaForm(request.POST, request.FILES)
        seo_form = SeoBlockForm1(request.POST)
        image_formset = GalleryImageFormSet(request.POST, request.FILES, queryset=Image1.objects.none())

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
        image_formset = GalleryImageFormSet(queryset=Image1.objects.none())

    context = {
        'form': form,
        'seo_form': seo_form,
        'gallery_formset': image_formset,
        'title': 'Создать новый кинотеатр',
        'is_create': True,
    }
    return render(request, 'cinema/admin_cinema_form.html', context)
