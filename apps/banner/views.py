from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import BannerSlider, BannerBackground, BottomBannerSlider
from .forms import (
    BannerSliderForm, BannerItemFormset, BannerBackgroundForm,
    BottomBannerSliderForm, BottomBannerItemFormset
)
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .models import BannerSlider, BannerBackground, BottomBannerSlider
from .forms import (
    BannerSliderForm, BannerItemFormset, BannerBackgroundForm,
    BottomBannerSliderForm, BottomBannerItemFormset
)


@method_decorator(staff_member_required, name='dispatch')
class BannerManagementView(TemplateView):
    template_name = 'banner/templates/admin_banner_management.html'

    def get(self, request, *args, **kwargs):
        # Для GET запроса просто показываем формы
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        # Определяем какая форма отправлена и обрабатываем её
        if 'save_top' in request.POST:
            return self.save_top_banner(request)
        elif 'save_background' in request.POST:
            return self.save_background(request)
        elif 'save_bottom' in request.POST:
            return self.save_bottom_banner(request)

        return redirect('banner_management')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем объекты
        top_slider = BannerSlider.objects.filter(is_active=True).first()
        bottom_slider = BottomBannerSlider.objects.filter(is_active=True).first()
        background = BannerBackground.objects.first()

        # Инициализируем формы
        context.update({
            'top_slider_form': BannerSliderForm(instance=top_slider, prefix='top'),
            'top_items_formset': BannerItemFormset(instance=top_slider, prefix='top_items'),
            'background_form': BannerBackgroundForm(instance=background, prefix='bg'),
            'bottom_slider_form': BottomBannerSliderForm(instance=bottom_slider, prefix='bottom'),
            'bottom_items_formset': BottomBannerItemFormset(instance=bottom_slider, prefix='bottom_items'),
            'title': 'Управление баннерами',
        })
        return context

    def save_top_banner(self, request):
        top_slider = BannerSlider.objects.filter(is_active=True).first()
        if not top_slider:
            top_slider = BannerSlider.objects.create(title="Верхний слайдер", is_active=True)

        top_slider_form = BannerSliderForm(request.POST, instance=top_slider, prefix='top')
        top_items_formset = BannerItemFormset(
            request.POST, request.FILES,
            instance=top_slider, prefix='top_items'
        )

        if top_slider_form.is_valid() and top_items_formset.is_valid():
            with transaction.atomic():
                slider = top_slider_form.save()
                top_items_formset.instance = slider
                top_items_formset.save()
            messages.success(request, 'Верхний баннер-слайдер успешно сохранён')
        else:
            messages.error(request, 'Ошибка сохранения верхнего баннера')

        return redirect('banner_management')

    def save_background(self, request):
        background = BannerBackground.objects.first()
        if not background:
            background = BannerBackground.objects.create(title="Фон")

        background_form = BannerBackgroundForm(
            request.POST, request.FILES,
            instance=background, prefix='bg'
        )

        if background_form.is_valid():
            background_form.save()
            messages.success(request, 'Фоновое изображение успешно сохранено')
        else:
            messages.error(request, 'Ошибка сохранения фона')

        return redirect('banner_management')

    def save_bottom_banner(self, request):
        bottom_slider = BottomBannerSlider.objects.filter(is_active=True).first()
        if not bottom_slider:
            bottom_slider = BottomBannerSlider.objects.create(title="Нижний слайдер", is_active=True)

        bottom_slider_form = BottomBannerSliderForm(
            request.POST, instance=bottom_slider, prefix='bottom'
        )
        bottom_items_formset = BottomBannerItemFormset(
            request.POST, request.FILES,
            instance=bottom_slider, prefix='bottom_items'
        )

        if bottom_slider_form.is_valid() and bottom_items_formset.is_valid():
            with transaction.atomic():
                slider = bottom_slider_form.save()
                bottom_items_formset.instance = slider
                bottom_items_formset.save()
            messages.success(request, 'Нижний баннер-слайдер успешно сохранён')
        else:
            messages.error(request, 'Ошибка сохранения нижнего баннера')

        return redirect('banner_management')