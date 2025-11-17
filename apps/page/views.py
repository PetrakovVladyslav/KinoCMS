from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.banner.models import BannerBackground, BannerSlider, BottomBannerSlider
from apps.cinema.models import Movie
from apps.core.forms import GalleryFormSet, SeoBlockForm
from apps.core.models import Gallery

from .forms import PageContactsForm, PageElseForm, PageMainForm, PageNewsSalesForm
from .models import PageContacts, PageElse, PageMain, PageNewsSales


def page_detail_view(request, slug):
    page = get_object_or_404(PageElse, slug=slug, status=True)

    context = {"page": page, "title": page.name}
    return render(request, "page/page_detail.html", context)


def home_view(request):
    today = timezone.localdate()
    today_movies = Movie.objects.filter(start_date__lte=today).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    )

    coming_soon_movies = Movie.objects.filter(start_date__gt=today)

    # Получаем данные о баннерах
    top_banner = BannerSlider.objects.filter(is_active=True).first()
    bottom_banner = BottomBannerSlider.objects.filter(is_active=True).first()
    background = BannerBackground.objects.first()

    # Получаем новости и акции
    news = PageNewsSales.objects.filter(type="news", status=True).order_by("-publish_date")[:3]
    sales = PageNewsSales.objects.filter(type="sale", status=True).order_by("-publish_date")[:3]

    context = {
        "today_movies": today_movies,
        "coming_soon_movies": coming_soon_movies,
        "today_date": today.strftime("%d.%B"),
        "top_banner": top_banner,
        "bottom_banner": bottom_banner,
        "background": background,
        "page_main": PageMain.objects.first(),
        "news": news,
        "sales": sales,
    }

    return render(request, "page/home.html", context)


def afisha_view(request):
    today = timezone.localdate()
    current_movies = Movie.objects.filter(start_date__lte=today).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    )

    context = {
        "movies": current_movies,
        "page_title": "Афиша",
    }

    return render(request, "page/afisha.html", context)


def soon_view(request):
    today = timezone.localdate()
    upcoming_movies = Movie.objects.filter(start_date__gt=today)

    context = {
        "movies": upcoming_movies,
        "page_title": "Скоро в прокате",
    }

    return render(request, "page/soon.html", context)


def contacts_view(request):
    # Только активные контакты, главный первый, затем по порядку
    contacts = PageContacts.objects.filter(status=True).order_by("-is_main", "order", "cinema_name")

    context = {"contacts": contacts, "title": "Кинотеатры"}
    return render(request, "page/contacts.html", context)


@staff_member_required(login_url="users:admin_login")
def main_page_view(request):
    """Редактирование главной страницы"""
    main_page = PageMain.objects.first()

    if not main_page:
        main_page = PageMain.objects.create(phone_number1="", phone_number2="", status=True)

    if request.method == "POST":
        form = PageMainForm(request.POST, request.FILES, instance=main_page)
        seo_form = SeoBlockForm(request.POST, instance=main_page.seo_block if main_page.seo_block else None)

        if form.is_valid() and seo_form.is_valid():
            main_page = form.save(commit=False)

            if seo_form.has_changed():
                seo_block = seo_form.save()
                main_page.seo_block = seo_block

            main_page.save()
            messages.success(request, "Главная страница обновлена")
            return redirect("page:admin_page_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageMainForm(instance=main_page)
        seo_form = SeoBlockForm(instance=main_page.seo_block if main_page.seo_block else None)

    context = {
        "form": form,
        "seo_form": seo_form,
        "title": "Главная страница",
    }
    return render(request, "page/admin_main_page_form.html", context)


@staff_member_required(login_url="users:admin_login")
def news_view(request):
    """Создание новости"""
    if request.method == "POST":
        form = PageNewsSalesForm(request.POST, request.FILES)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            news = form.save(commit=False)
            news.type = "news"

            if seo_form.has_changed():
                seo_block = seo_form.save()
                news.seo_block = seo_block

            news.save()

            # Галерея
            has_images = any(
                bool(f.cleaned_data.get("image"))
                for f in gallery_formset.forms
                if not f.cleaned_data.get("DELETE", False)
            )

            if has_images:
                gallery = Gallery.objects.create(name=f"Галерея - {news.name}")
                news.gallery = gallery
                news.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Новость "{news.name}" создана')
            return redirect("page:admin_news_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageNewsSalesForm()
        gallery_formset = GalleryFormSet()
        seo_form = SeoBlockForm()

    context = {
        "form": form,
        "gallery_formset": gallery_formset,
        "seo_form": seo_form,
        "title": "Создать новость",
        "is_create": True,
    }
    return render(request, "page/admin_news_form.html", context)


@staff_member_required(login_url="users:admin_login")
def sales_view(request):
    """Создание акции"""
    if request.method == "POST":
        form = PageNewsSalesForm(request.POST, request.FILES)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            sales = form.save(commit=False)
            sales.type = "sale"

            if seo_form.has_changed():
                seo_block = seo_form.save()
                sales.seo_block = seo_block

            sales.save()

            # Галерея
            has_images = any(
                bool(f.cleaned_data.get("image"))
                for f in gallery_formset.forms
                if not f.cleaned_data.get("DELETE", False)
            )

            if has_images:
                gallery = Gallery.objects.create(name=f"Галерея - {sales.name}")
                sales.gallery = gallery
                sales.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Акция "{sales.name}" создана')
            return redirect("page:admin_sales_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageNewsSalesForm()
        gallery_formset = GalleryFormSet()
        seo_form = SeoBlockForm()

    context = {
        "form": form,
        "gallery_formset": gallery_formset,
        "seo_form": seo_form,
        "title": "Создать акцию",
        "is_create": True,
    }
    return render(request, "page/admin_sales_form.html", context)


@staff_member_required(login_url="users:admin_login")
def admin_news_list_view(request):
    news_list = PageNewsSales.objects.filter(type="news").order_by("-date")

    context = {
        "news_list": news_list,
    }
    return render(request, "page/admin_news_list.html", context)


@staff_member_required(login_url="users:admin_login")
def news_update_view(request, news_id):
    news = get_object_or_404(PageNewsSales, pk=news_id, type="news")

    if request.method == "POST":
        form = PageNewsSalesForm(request.POST, request.FILES, instance=news)
        gallery_formset = GalleryFormSet(
            request.POST,
            request.FILES,
            instance=news.gallery if news.gallery_id else None,
        )
        seo_form = SeoBlockForm(request.POST, instance=news.seo_block if news.seo_block_id else None)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            # Сохраняем новость
            news = form.save(commit=False)
            news.type = "news"  # Устанавливаем тип

            # Сохраняем SEO
            if seo_form.has_changed():
                seo_block = seo_form.save()
                news.seo_block = seo_block

            # Галерея - создаем, если нужно
            has_images = any(
                bool(f.cleaned_data.get("image"))
                for f in gallery_formset.forms
                if not f.cleaned_data.get("DELETE", False)
            )

            if has_images and not news.gallery:
                gallery = Gallery.objects.create(name=f"Галерея - {news.name}")
                news.gallery = gallery
                gallery_formset.instance = gallery

            news.save()

            # Обновляем галерею
            if news.gallery:
                gallery_formset.save()

            messages.success(request, f'Новость "{news.name}" обновлена')
            return redirect("page:admin_news_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageNewsSalesForm(instance=news)
        gallery_formset = GalleryFormSet(instance=news.gallery if news.gallery_id else None)
        seo_form = SeoBlockForm(instance=news.seo_block if news.seo_block_id else None)

    context = {
        "form": form,
        "gallery_formset": gallery_formset,
        "seo_form": seo_form,
        "news": news,
        "title": f'Редактировать новость "{news.name}"',
        "is_create": False,
    }
    return render(request, "page/admin_news_form.html", context)


@staff_member_required(login_url="users:admin_login")
def news_delete_view(request, news_id):
    news = get_object_or_404(PageNewsSales, id=news_id, type="news")
    if request.method == "POST":
        news_name = news.name or news.name_ru

        if news.gallery:
            news.gallery.images.all().delete()
            news.gallery.delete()

        if news.seo_block:
            news.seo_block.delete()

        news.delete()
        messages.success(request, f'Новость "{news_name}" успешно удалена')
        return redirect("page:admin_news_list")
    else:
        messages.warning(request, "Некорректная попытка удаления страницы")
        return redirect("page:admin_news_list")


@staff_member_required(login_url="users:admin_login")
def admin_sales_list_view(request):
    sales_list = PageNewsSales.objects.filter(type="sale").order_by("-date")

    context = {
        "sales_list": sales_list,
    }
    return render(request, "page/admin_sales_list.html", context)


@staff_member_required(login_url="users:admin_login")
def sales_update_view(request, sales_id):
    sales = get_object_or_404(PageNewsSales, pk=sales_id, type="sale")

    if request.method == "POST":
        form = PageNewsSalesForm(request.POST, request.FILES, instance=sales)
        gallery_formset = GalleryFormSet(
            request.POST,
            request.FILES,
            instance=sales.gallery if sales.gallery_id else None,
        )
        seo_form = SeoBlockForm(request.POST, instance=sales.seo_block if sales.seo_block_id else None)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            sales = form.save(commit=False)
            sales.type = "sale"  # Устанавливаем тип

            if seo_form.has_changed():
                seo_block = seo_form.save()
                sales.seo_block = seo_block

            # Галерея - создаем, если нужно
            has_images = any(
                bool(f.cleaned_data.get("image"))
                for f in gallery_formset.forms
                if not f.cleaned_data.get("DELETE", False)
            )

            if has_images and not sales.gallery:
                gallery = Gallery.objects.create(name=f"Галерея - {sales.name}")
                sales.gallery = gallery
                gallery_formset.instance = gallery

            sales.save()

            if sales.gallery:
                gallery_formset.save()

            messages.success(request, f'Акция "{sales.name}" обновлена')
            return redirect("page:admin_sales_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageNewsSalesForm(instance=sales)
        gallery_formset = GalleryFormSet(instance=sales.gallery if sales.gallery_id else None)
        seo_form = SeoBlockForm(instance=sales.seo_block if sales.seo_block_id else None)

    context = {
        "form": form,
        "gallery_formset": gallery_formset,
        "seo_form": seo_form,
        "sales": sales,
        "title": f'Редактировать акцию "{sales.name}"',
        "is_create": False,
    }
    return render(request, "page/admin_sales_form.html", context)


@staff_member_required(login_url="users:admin_login")
def sales_delete_view(request, sales_id):
    sales = get_object_or_404(PageNewsSales, id=sales_id, type="sale")
    if request.method == "POST":
        sales_name = sales.name or sales.name_ru

        if sales.gallery:
            sales.gallery.images.all().delete()
            sales.gallery.delete()

        if sales.seo_block:
            sales.seo_block.delete()

        sales.delete()
        messages.success(request, f'Акция "{sales_name}" успешно удалена')
        return redirect("page:admin_sales_list")
    else:
        messages.warning(request, "Некорректная попытка удаления страницы")
        return redirect("page:admin_sales_list")


@staff_member_required(login_url="users:admin_login")
def sale_detail_view(request, item_id):
    item = get_object_or_404(PageNewsSales, pk=item_id, type__in=["sale", "news"], status=True)

    context = {
        "item": item,
        "title": item.name or item.name_ru,
    }
    return render(request, "page/sale_news_detail.html", context)


@staff_member_required(login_url="users:admin_login")
def sale_news_list_view(request):
    sales = PageNewsSales.objects.filter(type__in=["sale", "news"], status=True).order_by("-publish_date", "-date")

    context = {
        "sales": sales,
        "title": "Акции и скидки",
    }
    return render(request, "page/sale_news_list.html", context)


@staff_member_required(login_url="users:admin_login")
def contacts_admin_edit_view(request):
    """Упрощенный вариант - все в одной форме БЕЗ toggle"""

    main_contact = PageContacts.objects.filter(is_main=True).first()
    additional_contacts = PageContacts.objects.filter(is_main=False).order_by("order", "id")

    PageContactsFormSet = modelformset_factory(
        PageContacts,
        form=PageContactsForm,
        extra=0,  # Не создаём пустые формы автоматически
        can_delete=True,
    )

    if request.method == "POST":
        main_form = PageContactsForm(request.POST, request.FILES, instance=main_contact, prefix="main")
        formset = PageContactsFormSet(
            request.POST,
            request.FILES,
            queryset=additional_contacts,
            prefix="additional",
        )
        seo_form = SeoBlockForm(
            request.POST,
            instance=main_contact.seo_block if main_contact and main_contact.seo_block else None,
            prefix="seo",
        )

        if main_form.is_valid() and formset.is_valid() and seo_form.is_valid():
            # Сохраняем главный контакт
            main_contact = main_form.save(commit=False)
            main_contact.is_main = True
            main_contact.save()

            # Сохраняем дополнительные контакты и обрабатываем удаление
            for form in formset:
                if form.cleaned_data:
                    if form.cleaned_data.get("DELETE"):
                        # Удаляем объект, если он помечен для удаления
                        if form.instance.pk:
                            form.instance.delete()
                    else:
                        # Сохраняем объект
                        instance = form.save(commit=False)
                        instance.is_main = False
                        instance.save()

            # Сохраняем SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                main_contact.seo_block = seo_block
                main_contact.save()

            messages.success(request, "Все изменения сохранены!")
            return redirect("page:contacts")
        else:
            # Если есть ошибки, показываем их
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
            # Отладочный вывод ошибок
            if not main_form.is_valid():
                print("Main form errors:", main_form.errors)
            if not formset.is_valid():
                print("Formset errors:", formset.errors)
                for i, form in enumerate(formset):
                    if form.errors:
                        print(f"Form {i} errors:", form.errors)
            if not seo_form.is_valid():
                print("SEO form errors:", seo_form.errors)
    else:
        # Формы для GET запроса
        main_form = PageContactsForm(instance=main_contact, prefix="main")
        formset = PageContactsFormSet(queryset=additional_contacts, prefix="additional")
        seo_form = SeoBlockForm(
            instance=main_contact.seo_block if main_contact and main_contact.seo_block else None,
            prefix="seo",
        )

    context = {
        "main_form": main_form,
        "formset": formset,
        "seo_form": seo_form,
        "title": "Контакты кинотеатров",
    }

    return render(request, "page/admin_contacts_form.html", context)


@staff_member_required(login_url="users:admin_login")
def admin_page_list_view(request):
    """Просто показываем существующие страницы"""
    system_pages = PageElse.objects.filter(is_system=True).order_by("slug")
    user_pages = PageElse.objects.filter(is_system=False).order_by("-date")

    main_page = PageMain.objects.first()
    contacts = PageContacts.objects.filter(status=True).order_by("-is_main", "order")

    context = {
        "system_pages": system_pages,
        "user_pages": user_pages,
        "main_page": main_page,
        "contacts": contacts,
        "title": "Управление страницами",
    }
    return render(request, "page/admin_list.html", context)


@staff_member_required(login_url="users:admin_login")
def page_create_view(request):
    """Создание новой пользовательской страницы"""
    if request.method == "POST":
        form = PageElseForm(request.POST, request.FILES)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=None)
        seo_form = SeoBlockForm(request.POST)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            page = form.save(commit=False)
            page.is_system = False  # ✅ Это пользовательская страница

            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                page.seo_block = seo_block

            page.save()

            # Галерея
            has_images = any(
                bool(f.cleaned_data.get("image"))
                for f in gallery_formset.forms
                if not f.cleaned_data.get("DELETE", False)
            )

            if has_images:
                gallery = Gallery.objects.create(name=f"Галерея - {page.name}")
                page.gallery = gallery
                page.save()
                gallery_formset.instance = gallery
                gallery_formset.save()

            messages.success(request, f'Страница "{page.name}" создана')
            return redirect("page:admin_page_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageElseForm()
        gallery_formset = GalleryFormSet()
        seo_form = SeoBlockForm()

    context = {
        "form": form,
        "gallery_formset": gallery_formset,
        "seo_form": seo_form,
        "title": "Создать страницу",
        "is_create": True,
    }
    return render(request, "page/admin_system_page_form.html", context)


@staff_member_required(login_url="users:admin_login")
def page_update_view(request, pk):
    """Редактирование любой страницы"""
    page = get_object_or_404(PageElse, pk=pk)

    if request.method == "POST":
        form = PageElseForm(request.POST, request.FILES, instance=page)
        gallery_formset = GalleryFormSet(request.POST, request.FILES, instance=page.gallery)
        seo_form = SeoBlockForm(request.POST, instance=page.seo_block)

        if form.is_valid() and gallery_formset.is_valid() and seo_form.is_valid():
            page = form.save(commit=False)

            # SEO блок
            if seo_form.has_changed():
                seo_block = seo_form.save()
                page.seo_block = seo_block

            # Галерея - создаем, если нужно
            has_images = any(
                bool(f.cleaned_data.get("image"))
                for f in gallery_formset.forms
                if not f.cleaned_data.get("DELETE", False)
            )

            if has_images and not page.gallery:
                gallery = Gallery.objects.create(name=f"Галерея - {page.name}")
                page.gallery = gallery
                gallery_formset.instance = gallery

            page.save()

            # Сохраняем галерею
            if page.gallery:
                gallery_formset.save()

            messages.success(request, f'Страница "{page.name}" обновлена')
            return redirect("page:admin_page_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки")
    else:
        form = PageElseForm(instance=page)
        gallery_formset = GalleryFormSet(instance=page.gallery)
        seo_form = SeoBlockForm(instance=page.seo_block)

    context = {
        "form": form,
        "gallery_formset": gallery_formset,
        "seo_form": seo_form,
        "page": page,
        "title": f"Редактировать {page.name}",
        "is_system": page.is_system,
    }
    return render(request, "page/admin_system_page_form.html", context)


@staff_member_required(login_url="users:admin_login")
def page_delete_view(request, pk):
    """Удаление страницы (только пользовательских)"""
    page = get_object_or_404(PageElse, pk=pk)

    # Запрещаем удаление системных страниц
    if page.is_system:
        messages.error(request, "Нельзя удалять системные страницы")
        return redirect("page:admin_page_list")

    if request.method == "POST":
        page_name = page.name

        if page.gallery:
            page.gallery.images.all().delete()
            page.gallery.delete()

        if page.seo_block:
            page.seo_block.delete()

        page.delete()
        messages.success(request, f'Страница "{page_name}" успешно удалена')
        return redirect("page:admin_page_list")
    else:
        messages.warning(request, "Некорректная попытка удаления страницы")
        return redirect("page:admin_page_list")
