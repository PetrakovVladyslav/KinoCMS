from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse

from .models import PageMain, PageElse, PageContacts
from .forms import PageMainForm, PageElseForm, PageContactsForm


@staff_member_required(login_url='admin:login')
def main_page_view(request):
    """Редактирование главной страницы"""
    page_main = PageMain.objects.first()
    if not page_main:
        # Создаем главную страницу если её нет
        page_main = PageMain.objects.create(
            phone_number1='',
            phone_number2='',
            seo_text='',
        )
    
    if request.method == 'POST':
        form = PageMainForm(request.POST, request.FILES, instance=page_main)
        if form.is_valid():
            form.save()
            messages.success(request, 'Главная страница успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageMainForm(instance=page_main)
    
    context = {
        'form': form,
        'title': 'Редактировать главную страницу',
        'page': page_main,
    }
    return render(request, 'page/admin_main_page_form.html', context)


@staff_member_required(login_url='admin:login')
def coffee_bar_view(request):
    """Редактирование страницы Кафе-бар"""
    # Ищем страницу по названию или создаем новую
    page, created = PageElse.objects.get_or_create(
        name='Кафе-бар',
        defaults={
            'name_ru': 'Кафе-бар', 
            'name_uk': 'Кафе-бар',
            'description': '',
            'can_delete': False
        }
    )
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Страница "Кофе-бар" успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': 'Редактировать страницу "Кофе-бар"',
        'page': page,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def about_cinema_view(request):
    """Редактирование страницы О кинотеатре"""
    page, created = PageElse.objects.get_or_create(
        name='О кинотеатре',
        defaults={
            'name_ru': 'О кинотеатре', 
            'name_uk': 'Про кінотеатр',
            'description': '',
            'can_delete': False
        }
    )
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Страница "О кинотеатре" успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': 'Редактировать страницу "О кинотеатре"',
        'page': page,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def vip_hall_view(request):
    """Редактирование страницы VIP-зал"""
    page, created = PageElse.objects.get_or_create(
        name='VIP-зал',
        defaults={
            'name_ru': 'VIP-зал',
            'name_uk': 'VIP-зал', 
            'description': '',
            'can_delete': False
        }
    )
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Страница "VIP-зал" успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': 'Редактировать страницу "VIP-зал"',
        'page': page,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def advertising_view(request):
    """Редактирование страницы Реклама"""
    # Ищем страницу по названию или создаем новую
    try:
        page = PageElse.objects.get(name__icontains='реклам', can_delete=False)
    except PageElse.DoesNotExist:
        page = PageElse.objects.create(
            name='Реклама',
            name_ru='Реклама',
            name_uk='Реклама',
            description='',
            can_delete=False
        )
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Страница "Реклама" успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': 'Редактировать страницу "Реклама"',
        'page': page,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def children_room_view(request):
    """Редактирование страницы Детская комната"""
    page, created = PageElse.objects.get_or_create(
        name='Детская комната',
        defaults={
            'name_ru': 'Детская комната',
            'name_uk': 'Дитяча кімната',
            'description': '',
            'can_delete': False
        }
    )
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Страница "Детская комната" успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': 'Редактировать страницу "Детская комната"',
        'page': page,
    }
    return render(request, 'page/admin_page_form.html', context)
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Страница "Мобильные приложения" успешно обновлена')
            return redirect(request.path)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': 'Редактировать страницу "Мобильные приложения"',
        'page': page,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def contacts_view(request):
    """Редактирование страницы контактов"""
    contacts = PageContacts.objects.all()
    
    if request.method == 'POST':
        # Простая обработка: проходим по всем существующим контактам
        # и обновляем их, или создаем новые
        updated_count = 0
        
        for i, contact in enumerate(contacts):
            form = PageContactsForm(request.POST, request.FILES, instance=contact, prefix=str(i))
            if form.is_valid():
                form.save()
                updated_count += 1
        
        # Проверяем, есть ли данные для нового контакта
        new_form = PageContactsForm(request.POST, request.FILES, prefix='new')
        if new_form.is_valid() and new_form.cleaned_data.get('cinema_name'):
            new_form.save()
            updated_count += 1
        
        if updated_count > 0:
            messages.success(request, f'Обновлено {updated_count} контактов')
        else:
            messages.warning(request, 'Нет изменений для сохранения')
        
        return redirect(request.path)
    
    # GET request: создаем формы для существующих контактов + одну пустую для нового
    contact_forms = []
    for i, contact in enumerate(contacts):
        contact_forms.append(PageContactsForm(instance=contact, prefix=str(i)))
    
    # Добавляем пустую форму для нового контакта
    new_contact_form = PageContactsForm(prefix='new')
    
    context = {
        'contact_forms': contact_forms,
        'new_contact_form': new_contact_form,
        'title': 'Редактировать контакты',
        'contacts_count': len(contacts),
    }
    return render(request, 'page/admin_contacts_form.html', context)


@staff_member_required(login_url='admin:login')
def admin_list_view(request):
    """Список всех страниц для администрирования"""
    
    # Автоматически создаем системные страницы если их нет
    system_pages_config = [
        {'name': 'О кинотеатре', 'name_ru': 'О кинотеатре', 'name_uk': 'Про кінотеатр'},
        {'name': 'Кафе-бар', 'name_ru': 'Кафе-бар', 'name_uk': 'Кафе-бар'},
        {'name': 'VIP-зал', 'name_ru': 'VIP-зал', 'name_uk': 'VIP-зал'},
        {'name': 'Реклама', 'name_ru': 'Реклама', 'name_uk': 'Реклама'},
        {'name': 'Детская комната', 'name_ru': 'Детская комната', 'name_uk': 'Дитяча кімната'},
    ]
    
    for config in system_pages_config:
        PageElse.objects.get_or_create(
            name=config['name'],
            defaults={
                'name_ru': config['name_ru'],
                'name_uk': config['name_uk'],
                'description': '',
                'can_delete': False,
                'status': True
            }
        )
    
    # Получаем главную страницу
    main_page = PageMain.objects.first()
    if not main_page:
        main_page = PageMain.objects.create(
            phone_number1='',
            phone_number2='',
            seo_text='',
            status=True
        )
    
    # Получаем системные страницы
    system_pages = PageElse.objects.filter(can_delete=False)
    
    # Получаем пользовательские страницы 
    user_pages = PageElse.objects.filter(can_delete=True)
    
    # Получаем контакты (создаем по умолчанию если нет)
    contacts = PageContacts.objects.all()
    if not contacts.exists():
        PageContacts.objects.create(
            cinema_name='Кинотеатр',
            address='ул. Пример, 1',
            coordinates='',
            status=True
        )
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
        if form.is_valid():
            page = form.save(commit=False)
            page.can_delete = True  # Новые страницы можно удалять
            page.save()
            messages.success(request, f'Страница "{page.name}" успешно создана')
            return redirect('page:admin_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm()
    
    context = {
        'form': form,
        'title': 'Создать новую страницу',
        'is_create': True,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def page_update_view(request, pk):
    """Редактирование пользовательской страницы"""
    page = get_object_or_404(PageElse, pk=pk, can_delete=True)
    
    if request.method == 'POST':
        form = PageElseForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, f'Страница "{page.name}" успешно обновлена')
            return redirect('page:admin_list')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = PageElseForm(instance=page)
    
    context = {
        'form': form,
        'title': f'Редактировать страницу "{page.name}"',
        'page': page,
        'is_create': False,
    }
    return render(request, 'page/admin_page_form.html', context)


@staff_member_required(login_url='admin:login')
def page_delete_view(request, pk):
    """Удаление пользовательской страницы"""
    page = get_object_or_404(PageElse, pk=pk, can_delete=True)
    
    if request.method == 'POST':
        page_name = page.name
        page.delete()
        messages.success(request, f'Страница "{page_name}" успешно удалена')
        return redirect('page:admin_list')
    
    context = {
        'page': page,
        'title': f'Удалить страницу "{page.name}"',
    }
    return render(request, 'page/admin_page_delete.html', context)
