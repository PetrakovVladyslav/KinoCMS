from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.forms import formset_factory

from .models import PageMain, PageElse, PageContacts
from .forms import PageMainForm, PageElseForm, PageContactsForm, ImageFormSet, SeoBlockForm
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
# Это избавляет от дублирования кода и позволяет управлять страницами из одного места
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
    AdditionalContactsFormSet = formset_factory(
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
        additional_formset = AdditionalContactsFormSet(
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

        additional_formset = AdditionalContactsFormSet(
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

        if form.is_valid() and gallery_formset.is_valid():
            page = form.save(commit=False)
            page.can_delete = True
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

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
        'title': 'Создать новую страницу',
        'is_create': True,
    }
    return render(request, 'page/admin_system_page_form.html', context)


@staff_member_required(login_url='admin:login')
def page_update_view(request, pk):
    """Редактирование пользовательской страницы"""
    page = get_object_or_404(PageElse, pk=pk, can_delete=True)

    # Обеспечиваем наличие галереи
    ensure_gallery_for_page(page)

    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        gallery_formset = ImageFormSet(
            request.POST, request.FILES, instance=page.gallery
        )

        if form.is_valid() and gallery_formset.is_valid():
            form.save()
            gallery_formset.save()
            messages.success(request, f'Страница "{page.name}" успешно обновлена')
            return redirect('page:admin_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
        gallery_formset = ImageFormSet(instance=page.gallery)

    context = {
        'form': form,
        'gallery_formset': gallery_formset,
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