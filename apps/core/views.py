import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.cinema.models import Movie, Session
from apps.core.forms import MailingFileUploadForm
from apps.core.models import Mailing, MailingFile, MailingRecipient
from apps.core.tasks import send_mailing_task
from apps.users.forms import CustomUserUpdateForm
from apps.users.models import CustomUser, Gender

# Create your views here.


@staff_member_required(login_url="users:admin_login")
def admin_dashboard(request):
    # 1. Количество пользователей
    total_users = CustomUser.objects.count()

    # 2. Данные для графика сеансов
    today = timezone.now().date()
    sessions_data = []

    for i in range(7):
        date = today + timedelta(days=i)
        # Используем datetime напрямую
        date_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        date_end = timezone.make_aware(datetime.combine(date, datetime.max.time()))

        count = Session.objects.filter(start_time__gte=date_start, start_time__lte=date_end).count()
        sessions_data.append({"date": date.strftime("%d.%m"), "count": count})

    # 3. Статистика по полу
    gender_stats = CustomUser.objects.aggregate(
        male=Count("id", filter=Q(gender=Gender.MALE)), female=Count("id", filter=Q(gender=Gender.FEMALE))
    )

    total_gender = sum(gender_stats.values())
    if total_gender > 0:
        male_percent = round((gender_stats["male"] / total_gender) * 100, 1)
        female_percent = round((gender_stats["female"] / total_gender) * 100, 1)
    else:
        male_percent = female_percent = 0

    today = timezone.now().date()
    date_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    date_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))

    popular_movie = (
        Session.objects.filter(start_time__gte=date_start, start_time__lte=date_end)
        .values("movie__id", "movie__name")
        .annotate(sessions_count=Count("id"))
        .order_by("-sessions_count")
        .first()
    )

    print(f"Популярный фильм: {popular_movie}")

    gender_data = {
        "labels": ["Мужчины", "Женщины"],
        "data": [male_percent, female_percent],
        "counts": [gender_stats["male"], gender_stats["female"]],
        "colors": ["#3498db", "#e74c3c"],
    }

    context = {
        "total_users": total_users,
        "sessions_data": sessions_data,
        "gender_data": gender_data,
        "popular_movie": popular_movie,
    }

    return render(request, "core/admin_dashboard.html", context)


@staff_member_required(login_url="users:admin_login")
def admin_users_list(request):
    # Поиск
    search_query = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "-date_joined")
    allowed_sort_fields = [
        "id",
        "-id",
        "date_joined",
        "-date_joined",
        "date_of_birth",
        "-date_of_birth",
        "email",
        "-email",
        "phone_number",
        "-phone_number",
        "first_name",
        "-first_name",
        "last_name",
        "-last_name",
        "gender",
        "-gender",
        "city",
        "-city",
        "nickname",
        "-nickname",
    ]
    if sort_by not in allowed_sort_fields:
        sort_by = "-date_joined"
    users = CustomUser.objects.all().order_by(sort_by)

    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone_number__icontains=search_query)
            | Q(nickname__icontains=search_query)
        )

    # Пагинация
    paginator = Paginator(users, 10)  # 10 пользователей на страницу
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "users": page_obj,
        "search_query": search_query,
        "current_sort": sort_by,
        "total_users": users.count(),
    }
    return render(request, "core/admin_users_list.html", context)


@staff_member_required(login_url="users:admin_login")
def admin_user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Пользователь {user.get_full_name()} успешно обновлён")
            return redirect("core:admin_users_list")
        else:
            messages.error(request, "Ошибки в форме")
    else:
        form = CustomUserUpdateForm(instance=user)
        form.fields["gender"].initial = user.gender
        form.fields["language"].initial = user.language

    context = {
        "form": form,
        "user_obj": user,
    }
    return render(request, "core/admin_user_edit.html", context)


@staff_member_required(login_url="users:admin_login")
def admin_user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f"Пользователь {user_name} удалён")

        if request.headers.get("HX-Request"):
            return JsonResponse({"success": True})
        return redirect("core:admin_users_list")

    context = {
        "user_obj": user,
    }
    return render(request, "core/admin_user_delete.html", context)


def search_movies(request):
    """
    Живой поиск фильмов по названию (возвращает JSON)
    """
    query = request.GET.get("q", "").strip()
    results = []

    if query and len(query) >= 2:  # Начинаем поиск с 2 символов
        # Поиск по названию на русском и украинском языках
        # Только фильмы в прокате (start_date <= сегодня, end_date >= сегодня или не установлена)
        from django.utils import timezone

        today = timezone.now().date()

        movies = (
            Movie.objects.filter(Q(name_ru__icontains=query) | Q(name_uk__icontains=query))
            .filter(Q(start_date__lte=today) | Q(start_date__isnull=True))
            .filter(Q(end_date__gte=today) | Q(end_date__isnull=True))
            .distinct()[:10]
        )  # Ограничиваем 10 результатами

        for movie in movies:
            results.append(
                {
                    "id": movie.id,
                    "name": getattr(movie, "name_ru", movie.name),
                    "name_uk": getattr(movie, "name_uk", movie.name),
                    "poster": movie.poster.url if movie.poster else None,
                    "url": f"/movie/{movie.id}/",
                }
            )

    return JsonResponse({"results": results})


@staff_member_required(login_url="users:admin_login")
def admin_mailing(request):
    recent_files = MailingFile.objects.all()[:5]
    selected_user_ids = request.session.get("selected_users", [])
    active_mailing = Mailing.objects.filter(status__in=["pending", "processing"]).first()

    context = {
        "recent_files": recent_files,
        "selected_users_count": len(selected_user_ids),
        "total_users": CustomUser.objects.filter(is_active=True).count(),
        "active_mailing": active_mailing,
    }
    return render(request, "core/admin_mailing.html", context)


@staff_member_required(login_url="users:admin_login")
def admin_user_select(request):
    if request.method == "POST":
        selected_users = request.POST.getlist("selected_users")
        request.session["selected_users"] = [int(uid) for uid in selected_users]
        messages.success(request, f"Выбрано пользователей: {len(selected_users)}")
        return redirect("core:admin_mailing")

    search_query = request.GET.get("search", "")
    users = CustomUser.objects.filter(is_active=True).order_by("-date_joined")

    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "users": page_obj,
        "search_query": search_query,
        "selected_user_ids": request.session.get("selected_users", []),
    }
    return render(request, "core/admin_user_select.html", context)


@staff_member_required(login_url="users:admin_login")
def upload_mailing_file(request):
    if request.method == "POST":
        form = MailingFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            mailing_file = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "file_id": mailing_file.id,
                    "file_name": mailing_file.original_name,
                    "file_size": mailing_file.get_file_size_display(),
                }
            )
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse({"success": False}, status=400)


@staff_member_required(login_url="users:admin_login")
def delete_mailing_file(request, file_id):
    if request.method == "POST":
        try:
            MailingFile.objects.get(id=file_id).delete()
            return JsonResponse({"success": True})
        except MailingFile.DoesNotExist:
            return JsonResponse({"success": False}, status=404)
    return JsonResponse({"success": False}, status=400)


@staff_member_required(login_url="users:admin_login")
def start_mailing(request):
    logger = logging.getLogger(__name__)

    if request.method == "POST":
        file_id = request.POST.get("file_id")
        send_to_all = request.POST.get("send_to_all") == "true"

        # ВАЖНО: Проверяем что file_id передан
        if not file_id:
            return JsonResponse({"success": False, "error": "Не выбран файл"}, status=400)

        try:
            with transaction.atomic():
                mailing_file = MailingFile.objects.get(id=file_id)

                # Получаем пользователей
                if send_to_all:
                    users = CustomUser.objects.filter(is_active=True)
                else:
                    user_ids = request.session.get("selected_users", [])
                    if not user_ids:
                        return JsonResponse({"success": False, "error": "Не выбраны пользователи"}, status=400)
                    users = CustomUser.objects.filter(id__in=user_ids, is_active=True)

                # Создаем рассылку
                mailing = Mailing.objects.create(
                    file=mailing_file,
                    send_to_all=send_to_all,
                    total_recipients=users.count(),
                    status="pending",  # Явно устанавливаем статус
                )

                # Создаем получателей
                recipients = [MailingRecipient(mailing=mailing, user=user) for user in users]
                MailingRecipient.objects.bulk_create(recipients)

                # Запускаем задачу в фоне
                task = send_mailing_task.delay(mailing.id)

                # Сохраняем task_id в рассылке
                mailing.celery_task_id = task.id
                mailing.save(update_fields=["celery_task_id"])

                request.session.pop("selected_users", None)

                return JsonResponse(
                    {
                        "success": True,
                        "mailing_id": mailing.id,
                        "task_id": task.id,  # Возвращаем оба ID
                    }
                )

        except MailingFile.DoesNotExist:
            return JsonResponse({"success": False, "error": "Файл не найден"}, status=404)
        except Exception as e:
            logger.error(f"Error starting mailing: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid method"}, status=400)


@staff_member_required(login_url="users:admin_login")
def mailing_status(request, mailing_id):
    try:
        from celery.result import AsyncResult

        mailing = Mailing.objects.get(id=mailing_id)

        # Если задача еще выполняется - берем из Celery
        if mailing.celery_task_id and mailing.status == "processing":
            task = AsyncResult(mailing.celery_task_id)

            # Проверяем состояние задачи в Celery
            if task.state == "PROGRESS":
                # REAL-TIME данные из Redis
                return JsonResponse(
                    {
                        "status": "processing",
                        "progress": task.info.get("percent", 0),
                        "sent_count": task.info.get("sent", 0),
                        "failed_count": task.info.get("failed", 0),
                        "total_recipients": task.info.get("total", mailing.total_recipients),
                    }
                )

            elif task.state == "SUCCESS":
                # Задача завершена
                result = task.info
                return JsonResponse(
                    {
                        "status": "completed",
                        "progress": 100,
                        "sent_count": result.get("sent_count", mailing.sent_count),
                        "failed_count": result.get("failed_count", mailing.failed_count),
                        "total_recipients": mailing.total_recipients,
                    }
                )

            elif task.state == "FAILURE":
                return JsonResponse(
                    {"status": "failed", "error": str(task.info), "total_recipients": mailing.total_recipients}
                )

        return JsonResponse(
            {
                "status": mailing.status,
                "progress": mailing.get_progress_percentage(),
                "sent_count": mailing.sent_count,
                "failed_count": mailing.failed_count,
                "total_recipients": mailing.total_recipients,
            }
        )

    except Mailing.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
