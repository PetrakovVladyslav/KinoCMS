from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from django.forms import modelformset_factory

from apps.core.models import Gallery, GalleryImage, SeoBlock
from apps.core.forms import GalleryFormSet, SeoBlockForm



GalleryImageFormSet = inlineformset_factory(
    Gallery,
    Image,
    form=ImageForm,
    extra=1,
    can_delete=True
)
class PageFormMixin:
    model = Page
    form_class = PageForm
    template_name = "pages/form.html"
    success_url = reverse_lazy("pages:list")
    page_type = None  # переопределяется в наследнике

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['seo_form'] = SeoBlockForm(self.request.POST, instance=self.object.seo_block if self.object else None)
            ctx['gallery_formset'] = GalleryImageFormSet(self.request.POST, self.request.FILES,
                                                         instance=self.object.gallery if self.object else None)
        else:
            ctx['seo_form'] = SeoBlockForm(instance=self.object.seo_block if self.object else None)
            ctx['gallery_formset'] = GalleryImageFormSet(instance=self.object.gallery if self.object else None)
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        ctx = self.get_context_data()
        seo_form = ctx['seo_form']
        gallery_formset = ctx['gallery_formset']

        if not all([seo_form.is_valid(), gallery_formset.is_valid()]):
            return self.render_to_response(ctx)

        self.object = form.save(commit=False)
        self.object.type = self.page_type

        seo_block = seo_form.save()
        self.object.seo_block = seo_block

        if self.object.gallery is None:
            self.object.gallery = Gallery.objects.create(name=f'Галерея - {self.object.name}')
        self.object.save()
        form.save_m2m()

        gallery_formset.instance = self.object.gallery
        gallery_formset.save()

        messages.success(self.request, f'Страница "{self.object.name}" сохранена')
        return super().form_valid(form)


class NewsCreateView(PageFormMixin, CreateView):
    page_type = 'news'


class NewsUpdateView(PageFormMixin, UpdateView):
    page_type = 'news'


