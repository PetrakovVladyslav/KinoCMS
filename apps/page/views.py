from datetime import timezone
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from apps.cinema.models import Movie
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.forms import formset_factory
from django.db import models
from apps.core.models import Gallery
from .models import PageElse, PageContacts, PageNewsSales
from .forms import PageMainForm, PageElseForm, PageContactsForm, SeoBlockForm, PageNewsSalesForm
from apps.core.forms import GalleryFormSet








def home_view(request):
    today = timezone.localdate()
    today_movies = Movie.objects.filter(
        start_date__lte=today
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    )

    coming_soon_movies = Movie.objects.filter(start_date__gt=today)

    context = {
        'today_movies' : today_movies,
        'coming_soon_movies' : coming_soon_movies,
        'today_date' : today.strftime('%d.%B'),
    }

    return render(request, 'page/home.html', context)


def afisha_view(request):
    today = timezone.localdate()
    current_movies = Movie.objects.filter(
        start_date__lte=today
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    )

    context = {
        'movies': current_movies,
        'page_title': 'Афиша',
    }

    return render(request, 'page/afisha.html', context)


def soon_view(request):
    today = timezone.localdate()
    upcoming_movies = Movie.objects.filter(start_date__gt=today)

    context = {
        'movies': upcoming_movies,
        'page_title': 'Скоро в прокате',
    }

    return render(request, 'page/soon.html', context)




@staff_member_required(login_url='admin:login')
def admin_news_list_view(request):
    news_list = PageNewsSales.objects.filter(type='news').order_by('-date')
    
    context = {
        'news_list': news_list,
    }
    return render(request, 'page/admin_news_list.html', context)


@staff_member_required(login_url='admin:login')
def news_view(request):
    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            page = form.save(commit=False)
            page.type = 'news'  # Устанавливаем тип

            if seo_form.has_changed():
                seo_block = seo_form.save()
                page.seo_block = seo_block

            page.save()

            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if
                             not f.cleaned_data.get('DELETE', False))
            if has_images:
                from apps.core.models import Gallery
                gallery = Gallery.objects.create(name=f'Галерея - {page.name}')
                page.gallery = gallery
                page.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Новость "{page.name}" создана')
            return redirect('page:admin_news_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageNewsSalesForm()
        gallery_formset = GalleryFormSet()
        seo_form = SeoBlockForm()

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'title': 'Создать новость',
        'is_create': True,
    }
    return render(request, 'page/admin_news_form.html', context)


@staff_member_required(login_url='admin:login')
def news_update_view(request, news_id):

    news = get_object_or_404(PageNewsSales, pk=news_id, type='news')

    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES, instance=news)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=news.gallery if news.gallery_id else None)
        seo_form = SeoBlockForm(request.POST, instance=news.seo_block if news.seo_block_id else None)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            # Сохраняем новость
            news = form.save(commit=False)
            news.type = 'news'  # Устанавливаем тип

            # Сохраняем SEO
            if seo_form.has_changed():
                seo_block = seo_form.save()
                news.seo_block = seo_block

            news.save()

            # Обновляем галерею
            gallery_formset.save()

            messages.success(request, f'Новость "{news.name}" обновлена')
            return redirect('page:admin_news_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageNewsSalesForm(instance=news)
        gallery_formset = GalleryFormSet(instance=news.gallery if news.gallery_id else None)
        seo_form = SeoBlockForm(instance=news.seo_block if news.seo_block_id else None)

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'news': news,
        'title': f'Редактировать новость "{news.name}"',
        'is_create': False,
    }
    return render(request, 'page/admin_news_form.html', context)


@staff_member_required(login_url='admin:login')
def news_delete_view(request, news_id):

    news = get_object_or_404(PageNewsSales, id=news_id, type='news')
    if request.method == 'POST':
        news_name = news.name or news.name_ru

        if news.gallery:
            news.gallery.images.all().delete()
            news.gallery.delete()

        if news.seo_block:
            news.seo_block.delete()

        news.delete()
        messages.success(request, f'Новость "{news_name}" успешно удалена')
        return redirect('page:admin_news_list')
    else:
        messages.warning(request, 'Некорректная попытка удаления страницы')
        return redirect('page:admin_news_list')


@staff_member_required(login_url='admin:login')
def admin_sales_list_view(request):
    sales_list = PageNewsSales.objects.filter(type='sale').order_by('-date')

    context = {
        'sales_list': sales_list,
    }
    return render(request, 'page/admin_sales_list.html', context)


@staff_member_required(login_url='admin:login')
def sales_view(request):
    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            page = form.save(commit=False)
            page.type = 'sale'  # Устанавливаем тип

            if seo_form.has_changed():
                seo_block = seo_form.save()
                page.seo_block = seo_block

            page.save()

            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if
                             not f.cleaned_data.get('DELETE', False))
            if has_images:
                from apps.core.models import Gallery
                gallery = Gallery.objects.create(name=f'Галерея - {page.name}')
                page.gallery = gallery
                page.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Акция "{page.name}" создана')
            return redirect('page:admin_sales_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageNewsSalesForm()
        gallery_formset = GalleryFormSet()
        seo_form = SeoBlockForm()

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'title': 'Создать акцию',
        'is_create': True,
    }
    return render(request, 'page/admin_sales_form.html', context)


@staff_member_required(login_url='admin:login')
def sales_update_view(request, sales_id):
    sales = get_object_or_404(PageNewsSales, pk=sales_id, type='sale')

    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES, instance=sales)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=sales.gallery if sales.gallery_id else None)
        seo_form = SeoBlockForm(request.POST, instance=sales.seo_block if sales.seo_block_id else None)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            sales = form.save(commit=False)
            sales.type = 'sale'  # Устанавливаем тип

            if seo_form.has_changed():
                seo_block = seo_form.save()
                sales.seo_block = seo_block

            sales.save()

            gallery_formset.save()

            messages.success(request, f'Акция "{sales.name}" обновлена')
            return redirect('page:admin_sales_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageNewsSalesForm(instance=sales)
        gallery_formset = GalleryFormSet(instance=sales.gallery if sales.gallery_id else None)
        seo_form = SeoBlockForm(instance=sales.seo_block if sales.seo_block_id else None)

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'sales': sales,
        'title': f'Редактировать акцию "{sales.name}"',
        'is_create': False,
    }
    return render(request, 'page/admin_sales_form.html', context)




@staff_member_required(login_url='admin:login')
def sales_delete_view(request, sales_id):
    sales = get_object_or_404(PageNewsSales, id=news_id, type='sales')  # добавить фильтр по типу
    if request.method == 'POST':
        sales_name = sales.name or sales.name_ru

        if sales.gallery:
            sales.gallery.images.all().delete()
            sales.gallery.delete()

        if sales.seo_block:
            sales.seo_block.delete()

        sales.delete()
        messages.success(request, f'Акция "{sales_name}" успешно удалена')
        return redirect('page:admin_sales_list')
    else:
        messages.warning(request, 'Некорректная попытка удаления страницы')
        return redirect('page:admin_sales_list')


@staff_member_required(login_url='admin:login')
def sale_detail_view(request, item_id):
    item = get_object_or_404(
        PageNewsSales,
        pk=item_id,
        type__in=['sale', 'news'],
        status=True
    )

    context = {
        'item': item,
        'title': item.name or item.name_ru,
    }
    return render(request, 'page/sale_news_detail.html', context)


@staff_member_required(login_url='admin:login')
def sale_news_list_view(request):
    sales = PageNewsSales.objects.filter(
        type__in=['sale', 'news'],
        status=True
    ).order_by('-publish_date', '-date')

    context = {
        'sales': sales,
        'title': 'Акции и скидки',
    }
    return render(request, 'page/sale_news_list.html', context)
