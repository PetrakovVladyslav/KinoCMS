from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from apps.users.models import CustomUser
from apps.users.forms import CustomUserUpdateForm

# Create your views here.

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    context = {
        'total_movies': 42,
        'total_sessions': 156,
        'total_users': CustomUser.objects.count(),
        'total_pages': 8,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
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

@login_required
@user_passes_test(is_staff_user)
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

@login_required
@user_passes_test(is_staff_user)
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


