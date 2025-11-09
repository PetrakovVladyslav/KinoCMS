from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from apps.users.models import CustomUser
from apps.users.forms import CustomUserUpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from apps.cinema.models import Movie


# Create your views here.


@staff_member_required(login_url='admin:login')

def admin_dashboard(request):
    context = {
        'total_movies': 42,
        'total_sessions': 156,
        'total_users': CustomUser.objects.count(),
        'total_pages': 8,
    }
    return render(request, 'core/admin_dashboard.html', context)

@staff_member_required(login_url='admin:login')

def admin_users_list(request):
    # Поиск
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-date_joined')
    allowed_sort_fields = [
        'id', '-id',
        'date_joined', '-date_joined',
        'date_of_birth', '-date_of_birth',
        'email', '-email',
        'phone_number', '-phone_number',
        'first_name', '-first_name',
        'last_name', '-last_name',
        'gender', '-gender',
        'city', '-city'
    ]
    if sort_by not in allowed_sort_fields:
        sort_by = '-date_joined'
    users = CustomUser.objects.all().order_by(sort_by)

    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(users, 10)  # 10 пользователей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
        'current_sort': sort_by,
        'total_users': users.count(),
    }
    return render(request, 'core/admin_users_list.html', context)

@staff_member_required(login_url='admin:login')

def admin_user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Пользователь {user.get_full_name()} успешно обновлён')
            return redirect('core:admin_users_list')
        else:
            messages.error(request, 'Ошибки в форме')
    else:
        form = CustomUserUpdateForm(instance=user)
        form.fields['gender'].initial = user.gender
        form.fields['language'].initial = user.language
    
    context = {
        'form': form,
        'user_obj': user,
    }
    return render(request, 'core/admin_user_edit.html', context)

@staff_member_required(login_url='admin:login')

def admin_user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f'Пользователь {user_name} удалён')
        
        if request.headers.get('HX-Request'):
            return JsonResponse({'success': True})
        return redirect('core:admin_users_list')
    
    context = {
        'user_obj': user,
    }
    return render(request, 'core/admin_user_delete.html', context)


def search_movies(request):
    """
    Живой поиск фильмов по названию (возвращает JSON)
    """
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:  # Начинаем поиск с 2 символов
        # Поиск по названию на русском и украинском языках
        # Только фильмы в прокате (start_date <= сегодня, end_date >= сегодня или не установлена)
        from django.utils import timezone
        today = timezone.now().date()
        
        movies = Movie.objects.filter(
            Q(name_ru__icontains=query) | Q(name_uk__icontains=query)
        ).filter(
            Q(start_date__lte=today) | Q(start_date__isnull=True)
        ).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        ).distinct()[:10]  # Ограничиваем 10 результатами
        
        for movie in movies:
            results.append({
                'id': movie.id,
                'name': getattr(movie, 'name_ru', movie.name),
                'name_uk': getattr(movie, 'name_uk', movie.name),
                'poster': movie.poster.url if movie.poster else None,
                'url': f'/movie/{movie.id}/',
            })
    
    return JsonResponse({'results': results})

