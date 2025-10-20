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
from apps.core.forms import ImageFormSet
from .utils import (
    ensure_gallery_for_page,
    ensure_seo_block_for_page,
    ensure_seo_block_for_main_page,
    ensure_seo_block_for_contacts_page,
    get_or_create_main_contact,
    get_or_create_main_page,
    ensure_system_pages,
    SYSTEM_PAGES_CONFIG,
)



def system_page_view_factory(page_name: str, name_ru: str, name_uk: str, template_title: str):


    @staff_member_required(login_url='admin:login')
    def view(request):
        # Получаем или создаем страницу
        page, created = PageElse.objects.get_or_create(
            name=page_name,
            defaults={
                'name_ru': name_ru,
                'name_uk': name_uk,
                'description': '',
                'can_delete': False
            }
        )

        # Обеспечиваем наличие галереи и SEO-блока
        ensure_gallery_for_page(page)
        ensure_seo_block_for_page(page)

        if request.method == 'POST':
            form = PageElseForm(request.POST, request.FILES, instance=page)
            gallery_formset = ImageFormSet(
                request.POST, request.FILES, instance=page.gallery
            )
            seo_form = SeoBlockForm(request.POST, instance=page.seo_block)

            if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
                form.save()
                gallery_formset.save()
                seo_form.save()
                messages.success(request, f'Страница "{page_name}" успешно обновлена')
                return redirect(request.path)
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
        else:
            form = PageElseForm(instance=page)
            gallery_formset = ImageFormSet(instance=page.gallery)
            seo_form = SeoBlockForm(instance=page.seo_block)

        context = {
            'form': form,
            'gallery_formset': gallery_formset,
            'seo_form': seo_form,
            'title': template_title,
            'page': page,
        }
        return render(request, 'page/admin_system_page_form.html', context)

    return view


# Создаем системные представления из конфигурации

_system_views = {}
for config in SYSTEM_PAGES_CONFIG:
    view_name = config['name'].lower().replace(' ', '_').replace('-', '_')
    _system_views[view_name] = system_page_view_factory(
        config['name'],
        config['name_ru'],
        config['name_uk'],
        config['template_title']
    )

coffee_bar_view = _system_views.get('кафе_бар')
about_cinema_view = _system_views.get('о_кинотеатре')
vip_hall_view = _system_views.get('vip_зал')
advertising_view = _system_views.get('реклама')
children_room_view = _system_views.get('детская_комната')



@staff_member_required(login_url='admin:login')
def main_page_view(request):
    page_main = get_or_create_main_page()

    # Обеспечиваем наличие SEO-блока
    ensure_seo_block_for_main_page(page_main)

    if request.method == 'POST':
        form = PageMainForm(request.POST, request.FILES, instance=page_main)
        seo_form = SeoBlockForm(request.POST, instance=page_main.seo_block)

        if form.is_valid() and seo_form.is_valid():
            form.save()
            seo_form.save()
            messages.success(request, 'Главная страница успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageMainForm(instance=page_main)
        seo_form = SeoBlockForm(instance=page_main.seo_block)

    context = {
        'form': form,
        'seo_form': seo_form,
        'title': 'Редактировать главную страницу',
        'page': page_main,
    }
    return render(request, 'page/admin_main_page_form.html', context)




@staff_member_required(login_url='admin:login')
def contacts_view(request):

    main_contact = get_or_create_main_contact()

    # Обеспечиваем наличие SEO блока
    seo_block = ensure_seo_block_for_contacts_page()

    # Получаем дополнительные контакты (все кроме первого)
    additional_contacts = PageContacts.objects.exclude(pk=main_contact.pk)

    # Создаем formset для дополнительных контактов
    additional_contacts_formset_class = formset_factory(
        PageContactsForm,
        extra=1,
        can_delete=True,
        max_num=10
    )

    if request.method == 'POST':
        # Обрабатываем формы
        main_form = PageContactsForm(
            request.POST, request.FILES, instance=main_contact, prefix='main'
        )
        additional_formset = additional_contacts_formset_class(
            request.POST, request.FILES, prefix='additional'
        )
        seo_form = SeoBlockForm(request.POST, instance=seo_block)

        if main_form.is_valid() and additional_formset.is_valid() and seo_form.is_valid():
            # Сохраняем главный контакт и SEO
            main_form.save()
            seo_form.save()

            # Удаляем старые дополнительные контакты
            additional_contacts.delete()

            # Сохраняем новые дополнительные контакты
            for form in additional_formset:
                if form.is_valid() and not form.cleaned_data.get('DELETE', False):
                    if form.cleaned_data.get('cinema_name'):
                        contact = form.save(commit=False)
                        contact.status = True
                        contact.save()

            messages.success(request, 'Контакты успешно обновлены')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')

    else:
        # GET request: создаем формы
        main_form = PageContactsForm(instance=main_contact, prefix='main')

        # Подготавливаем данные для formset дополнительных контактов
        initial_additional = [
            {
                'cinema_name': contact.cinema_name,
                'address': contact.address,
                'coordinates': contact.coordinates,
                'logo': contact.logo,
            }
            for contact in additional_contacts
        ]

        additional_formset = additional_contacts_formset_class(
            initial=initial_additional,
            prefix='additional'
        )
        seo_form = SeoBlockForm(instance=seo_block)

    context = {
        'main_form': main_form,
        'additional_formset': additional_formset,
        'seo_form': seo_form,
        'main_contact': main_contact,
        'title': 'Редактировать контакты',
    }
    return render(request, 'page/admin_contacts_form.html', context)



@staff_member_required(login_url='admin:login')
def admin_list_view(request):
    # Вызываем ensure_system_pages только если нет системных страниц
    if not PageElse.objects.filter(can_delete=False).exists():
        ensure_system_pages()

    main_page = get_or_create_main_page()

    # Получаем страницы с оптимизацией запросов
    system_pages = PageElse.objects.filter(
        can_delete=False
    ).select_related('seo_block', 'gallery')

    user_pages = PageElse.objects.filter(
        can_delete=True
    ).select_related('seo_block', 'gallery')

    # Получаем контакты
    contacts = PageContacts.objects.all()
    if not contacts.exists():
        get_or_create_main_contact()
        contacts = PageContacts.objects.all()

    context = {
        'main_page': main_page,
        'system_pages': system_pages,
        'user_pages': user_pages,
        'contacts': contacts,
        'title': 'Управление страницами',
    }
    return render(request, 'page/admin_list.html', context)




@staff_member_required(login_url='admin:login')
def page_create_view(request):
    """Создание новой пользовательской страницы"""
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES)
        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            page = form.save(commit=False)
            page.can_delete = True
            
            # Сохраняем SEO если есть данные
            if seo_form.has_changed():
                seo_block = seo_form.save()
                page.seo_block = seo_block
            
            page.save()

            # Создаем галерею и присваиваем формсету
            ensure_gallery_for_page(page)
            gallery_formset.instance = page.gallery
            gallery_formset.save()

            messages.success(request, f'Страница "{page.name}" успешно создана')
            return redirect('page:admin_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm()
        gallery_formset = ImageFormSet(instance=None)
        seo_form = SeoBlockForm()

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'title': 'Создать новую страницу',
        'is_create': True,
    }
    return render(request, 'page/admin_system_page_form.html', context)


@staff_member_required(login_url='admin:login')
def page_update_view(request, pk):
    """Редактирование пользовательской страницы"""
    page = get_object_or_404(PageElse, pk=pk, can_delete=True)

    # Обеспечиваем наличие галереи и SEO-блока
    ensure_gallery_for_page(page)
    ensure_seo_block_for_page(page)

    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        gallery_formset = ImageFormSet(
            request.POST, request.FILES, instance=page.gallery
        )
        seo_form = SeoBlockForm(request.POST, instance=page.seo_block)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            form.save()
            gallery_formset.save()
            seo_form.save()
            messages.success(request, f'Страница "{page.name}" успешно обновлена')
            return redirect('page:admin_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
        gallery_formset = ImageFormSet(instance=page.gallery)
        seo_form = SeoBlockForm(instance=page.seo_block)

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'title': f'Редактировать страницу "{page.name}"',
        'page': page,
        'is_create': False,
    }
    return render(request, 'page/admin_system_page_form.html', context)


@staff_member_required(login_url='admin:login')
def page_delete_view(request, pk):

    #Удаление пользовательской страницы
    page = get_object_or_404(PageElse, pk=pk, can_delete=True)

    if request.method == 'POST':
        page_name = page.name
        page.delete()
        messages.success(request, f'Страница "{page_name}" успешно удалена')
        return redirect('page:admin_list')
    else:
        messages.warning(request, 'Некорректная попытка удаления страницы')
        return redirect('page:admin_list')




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
    """Страница афиши - фильмы в прокате"""
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
    """Страница скоро в прокате"""
    today = timezone.localdate()
    upcoming_movies = Movie.objects.filter(start_date__gt=today)

    context = {
        'movies': upcoming_movies,
        'page_title': 'Скоро в прокате',
    }

    return render(request, 'page/soon.html', context)


@staff_member_required(login_url='admin:login')
def sales_view(request):
    """Страница акций"""
    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES)
        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)
        
        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            # Сохраняем акцию
            page = form.save(commit=False)
            page.type = 'sale'  # Устанавливаем тип
            
            # Сохраняем SEO
            if seo_form.has_changed():
                seo_block = seo_form.save()
                page.seo_block = seo_block
            
            page.save()
            
            # Создаем галерею если есть изображения
            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if not f.cleaned_data.get('DELETE', False))
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
        gallery_formset = ImageFormSet()
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
def news_view(request):
    """Страница новостей"""
    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES)
        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            # Сохраняем новость
            news = form.save(commit=False)
            news.type = 'news'  # Устанавливаем тип
            news.can_delete = True
            # Сохраняем SEO
            if seo_form.has_changed():
                seo_block = seo_form.save()
                news.seo_block = seo_block

            news.save()

            # Создаем галерею если есть изображения
            has_images = any(bool(f.cleaned_data.get('image')) for f in gallery_formset.forms if not f.cleaned_data.get('DELETE', False))
            if has_images:
                gallery = Gallery.objects.create(name=f'Галерея - {news.name}')
                news.gallery = gallery
                news.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Новость "{news.name}" создана')
            return redirect('page:admin_news_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageNewsSalesForm()
        gallery_formset = ImageFormSet()
        seo_form = SeoBlockForm()

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'seo_form': seo_form,
        'title': 'Создать новость',
        'is_create': True,
    }
    return render(request, 'page/admin_news_form.html', context)
#fdfsadasd sdsdasdasd

'''
def home_view(request):
    # Получаем данные главной страницы
    try:
        page_main = PageMain.objects.filter(status=True).first()
    except PageMain.DoesNotExist:
        page_main = None

    # Получаем фильмы (пока все, потом можно будет фильтровать по датам)
    today_movies = Movie.objects.all()[:6]  # Первые 6 фильмов для "сегодня"
    coming_soon_movies = Movie.objects.all()[6:12]  # Следующие 6 для "скоро"

    # Текущая дата
    today_date = timezone.now().strftime('%d %B')

    context = {
        'page_main': page_main,  # Нужно для header и для содержимого
        'today_movies': today_movies,
        'coming_soon_movies': coming_soon_movies,
        'today_date': today_date,
    }
    return render(request, 'page/home.html', context)
'''


@staff_member_required(login_url='admin:login')
def admin_news_list_view(request):
    """Список новостей"""
    news_list = PageNewsSales.objects.filter(type='news').order_by('-date')
    
    context = {
        'news_list': news_list,
    }
    return render(request, 'page/admin_news_list.html', context)

@staff_member_required(login_url='admin:login')
def news_update_view(request, news_id):

    news = get_object_or_404(PageNewsSales, pk=news_id, type='news')

    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES, instance=news)
        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=news.gallery if news.gallery_id else None)
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
        gallery_formset = ImageFormSet(instance=news.gallery if news.gallery_id else None)
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

    news = get_object_or_404(PageNewsSales, id=news_id)

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
    """Список акций"""
    sales_list = PageNewsSales.objects.filter(type='sale').order_by('-date')
    
    context = {
        'sales_list': sales_list,
    }
    return render(request, 'page/admin_sales_list.html', context)






@staff_member_required(login_url='admin:login')
def sales_update_view(request, sales_id):
    sales = get_object_or_404(PageNewsSales, pk=sales_id, type='sale')

    if request.method == 'POST':
        form = PageNewsSalesForm(request.POST, request.FILES, instance=sales)
        gallery_formset = ImageFormSet(request.POST, request.FILES, instance=sales.gallery if sales.gallery_id else None)
        seo_form = SeoBlockForm(request.POST, instance=sales.seo_block if sales.seo_block_id else None)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            # Сохраняем акцию
            sales = form.save(commit=False)
            sales.type = 'sale'  # Устанавливаем тип

            # Сохраняем SEO
            if seo_form.has_changed():
                seo_block = seo_form.save()
                sales.seo_block = seo_block

            sales.save()

            # Обновляем галерею
            gallery_formset.save()

            messages.success(request, f'Акция "{sales.name}" обновлена')
            return redirect('page:admin_sales_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки')
    else:
        form = PageNewsSalesForm(instance=sales)
        gallery_formset = ImageFormSet(instance=sales.gallery if sales.gallery_id else None)
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


def sale_news_list_view(request):
    """Список акций и новостей"""
    sales = PageNewsSales.objects.filter(
        type__in=['sale', 'news'],
        status=True
    ).order_by('-publish_date', '-date')

    context = {
        'sales': sales,
        'title': 'Акции и скидки',
    }
    return render(request, 'page/sale_news_list.html', context)


def sale_detail_view(request, item_id):
    """Детальная страница акции или новости"""
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
def sales_delete_view(request, sales_id):
    sales = get_object_or_404(PageNewsSales, id=sales_id)

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

