from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.db import models

from .models import PageMain, PageElse, PageContacts
from .forms import PageMainForm, PageElseForm, ContactsForm, ContactsFormSet, SeoForm, GalleryForm, ImageInlineFormset
from apps.core.models import SeoBlock, Gallery, Image


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff access"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class PageListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Объединенный список всех страниц"""
    template_name = 'page/admin_list.html'
    context_object_name = 'pages'
    paginate_by = 10

    def get_queryset(self):
        # Объединяем все типы страниц в один список
        main_pages = PageMain.objects.all().annotate(
            page_type=models.Value('main', models.CharField())
        )
        else_pages = PageElse.objects.all().annotate(
            page_type=models.Value('else', models.CharField())
        )
        contacts_pages = PageContacts.objects.all().annotate(
            page_type=models.Value('contacts', models.CharField())
        )
        
        # Создаем список объектов с унифицированными полями
        all_pages = []
        
        for page in main_pages:
            all_pages.append({
                'id': page.id,
                'name': 'Главная страница',
                'type': 'main',
                'date': page.date,
                'status': page.status,
                'model': 'main'
            })
            
        for page in else_pages:
            # Use translated name fields, fallback to base name field, then default
            name = (getattr(page, 'name_ru', None) or 
                   getattr(page, 'name_uk', None) or 
                   getattr(page, 'name', None) or 
                   'Без названия')
            # Если название пустая строка, заменяем на дефолтное
            if not name.strip():
                name = 'Без названия'
            all_pages.append({
                'id': page.id,
                'name': name,
                'type': 'else',
                'date': page.date,
                'status': page.status,
                'model': 'else',
                'can_delete': page.can_delete
            })
            
        # Show only one Contacts entry regardless of how many cinema contacts exist
        if contacts_pages.exists():
            first_contact = contacts_pages.first()
            all_pages.append({
                'id': first_contact.id,  # Use first contact ID for URL
                'name': 'Контакты',  # Static name for contacts page
                'type': 'contacts',
                'date': first_contact.date,
                'status': any(p.status for p in contacts_pages),  # Active if any contact is active
                'model': 'contacts'
            })
            
        # Сортируем по дате создания
        all_pages.sort(key=lambda x: x['date'], reverse=True)
        return all_pages


# Views для PageMain
class PageMainUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = PageMain
    form_class = PageMainForm
    template_name = 'page/admin_form.html'
    success_url = reverse_lazy('page:admin_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать главную страницу'
        context['is_create'] = False
        context['show_language_switcher'] = True  # PageMain has multilingual seo_text
        
        # Get or create SEO block
        if self.object.seo_block:
            seo_block = self.object.seo_block
        else:
            seo_block = SeoBlock()
        context['seo_form'] = SeoForm(instance=seo_block)
        
        # Get or create Gallery (PageMain doesn't have gallery, so skip it)
        context['gallery_form'] = GalleryForm()
        context['image_formset'] = ImageInlineFormset(queryset=Image.objects.none())
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        # Get or create SEO block
        if self.object.seo_block:
            seo_block = self.object.seo_block
        else:
            seo_block = SeoBlock()
        seo_form = SeoForm(request.POST, instance=seo_block)
        
        # PageMain doesn't have gallery, so create empty forms
        gallery_form = GalleryForm()
        image_formset = ImageInlineFormset()
        
        if form.is_valid() and seo_form.is_valid():
            return self.form_valid(form, seo_form, gallery_form, image_formset)
        else:
            return self.form_invalid(form, seo_form, gallery_form, image_formset)
    
    def form_valid(self, form, seo_form, gallery_form, image_formset):
        # Save main form
        response = super().form_valid(form)
        
        # Save SEO form if it has data
        if seo_form.is_valid():
            # Check if any SEO fields have data
            has_seo_data = any([
                seo_form.cleaned_data.get('title'),
                seo_form.cleaned_data.get('keywords'),
                seo_form.cleaned_data.get('description'),
                seo_form.cleaned_data.get('url')
            ])
            
            if has_seo_data:
                seo_block = seo_form.save()
                # Link SEO block to the page object
                self.object.seo_block = seo_block
                self.object.save(update_fields=['seo_block'])
        
        # PageMain doesn't have gallery, so we skip gallery and images
        
        messages.success(self.request, 'Главная страница успешно обновлена')
        return response
    
    def form_invalid(self, form, seo_form, gallery_form, image_formset):
        context = self.get_context_data()
        context['form'] = form
        context['seo_form'] = seo_form
        context['gallery_form'] = gallery_form
        context['image_formset'] = image_formset
        return self.render_to_response(context)


# Views для PageElse
class PageElseCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = PageElse
    form_class = PageElseForm
    template_name = 'page/admin_form.html'
    success_url = reverse_lazy('page:admin_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать новую страницу'
        context['is_create'] = True
        context['show_language_switcher'] = True  # PageElse has multilingual name and description
        
        # Empty forms for create
        context['seo_form'] = SeoForm()
        context['gallery_form'] = GalleryForm()
        context['image_formset'] = ImageInlineFormset(queryset=Image.objects.none())
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        
        # Create forms
        seo_form = SeoForm(request.POST)
        gallery_form = GalleryForm(request.POST)
        image_formset = ImageInlineFormset(request.POST, request.FILES)
        
        if form.is_valid() and seo_form.is_valid() and gallery_form.is_valid() and image_formset.is_valid():
            return self.form_valid(form, seo_form, gallery_form, image_formset)
        else:
            return self.form_invalid(form, seo_form, gallery_form, image_formset)
    
    def form_valid(self, form, seo_form, gallery_form, image_formset):
        # Устанавливаем can_delete=True для новых страниц
        form.instance.can_delete = True
        
        # Save main form first
        response = super().form_valid(form)
        
        # Save SEO form if it has data
        if seo_form.is_valid():
            # Check if any SEO fields have data
            has_seo_data = any([
                seo_form.cleaned_data.get('title'),
                seo_form.cleaned_data.get('keywords'),
                seo_form.cleaned_data.get('description'),
                seo_form.cleaned_data.get('url')
            ])
            
            if has_seo_data:
                seo_block = seo_form.save()
                # Link SEO block to the page object
                self.object.seo_block = seo_block
                self.object.save(update_fields=['seo_block'])
        
        # Save Gallery and images if we have any images
        if image_formset.is_valid():
            images_to_save = []
            for img_form in image_formset:
                if img_form.cleaned_data and not img_form.cleaned_data.get('DELETE', False):
                    if img_form.cleaned_data.get('image'):
                        images_to_save.append(img_form)
            
            if images_to_save:
                # Create gallery for new page
                gallery = Gallery.objects.create(name=f'Gallery-{self.object.pk}')
                self.object.gallery = gallery
                self.object.save(update_fields=['gallery'])
                
                # Save images
                images = image_formset.save(commit=False)
                for image in images:
                    if image.image:  # Only save if image is present
                        image.gallery = gallery
                        image.save()
        
        messages.success(self.request, f'Страница "{self.object.name}" успешно создана')
        return response
    
    def form_invalid(self, form, seo_form, gallery_form, image_formset):
        context = self.get_context_data()
        context['form'] = form
        context['seo_form'] = seo_form
        context['gallery_form'] = gallery_form
        context['image_formset'] = image_formset
        return self.render_to_response(context)


class PageElseUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = PageElse
    form_class = PageElseForm
    template_name = 'page/admin_form.html'
    success_url = reverse_lazy('page:admin_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Генерируем название страницы
        page_name = (getattr(self.object, 'name_ru', None) or 
                    getattr(self.object, 'name_uk', None) or 
                    getattr(self.object, 'name', None) or 
                    'Без названия')
        if not page_name.strip():
            page_name = 'Без названия'
        context['title'] = f'Редактировать страницу "{page_name}"'
        context['is_create'] = False
        context['show_language_switcher'] = True  # PageElse has multilingual name and description
        
        # Get or create SEO block
        if self.object.seo_block:
            seo_block = self.object.seo_block
        else:
            seo_block = SeoBlock()
        context['seo_form'] = SeoForm(instance=seo_block)
        
        # Get or create Gallery
        if self.object.gallery:
            gallery = self.object.gallery
            images = gallery.images.all()
        else:
            gallery = Gallery()
            images = Image.objects.none()
        context['gallery_form'] = GalleryForm(instance=gallery)
        context['image_formset'] = ImageInlineFormset(queryset=images)
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        # Get or create SEO block
        if self.object.seo_block:
            seo_block = self.object.seo_block
        else:
            seo_block = SeoBlock()
        seo_form = SeoForm(request.POST, instance=seo_block)
        
        # Get or create Gallery
        if self.object.gallery:
            gallery = self.object.gallery
        else:
            gallery = Gallery()
        gallery_form = GalleryForm(request.POST, instance=gallery)
        
        # Image formset
        if self.object.gallery:
            image_formset = ImageInlineFormset(request.POST, request.FILES, queryset=self.object.gallery.images.all())
        else:
            image_formset = ImageInlineFormset(request.POST, request.FILES, queryset=Image.objects.none())
        
        if form.is_valid() and seo_form.is_valid() and gallery_form.is_valid() and image_formset.is_valid():
            return self.form_valid(form, seo_form, gallery_form, image_formset)
        else:
            return self.form_invalid(form, seo_form, gallery_form, image_formset)
    
    def form_valid(self, form, seo_form, gallery_form, image_formset):
        # Save main form
        response = super().form_valid(form)
        
        # Save SEO form if it has data
        if seo_form.is_valid():
            # Check if any SEO fields have data
            has_seo_data = any([
                seo_form.cleaned_data.get('title'),
                seo_form.cleaned_data.get('keywords'),
                seo_form.cleaned_data.get('description'),
                seo_form.cleaned_data.get('url')
            ])
            
            if has_seo_data:
                seo_block = seo_form.save()
                # Link SEO block to the page object
                self.object.seo_block = seo_block
                self.object.save(update_fields=['seo_block'])
        
        # Save Gallery and images if we have any images
        if image_formset.is_valid():
            images_to_save = []
            for img_form in image_formset:
                if img_form.cleaned_data and not img_form.cleaned_data.get('DELETE', False):
                    if img_form.cleaned_data.get('image'):
                        images_to_save.append(img_form)
            
            if images_to_save:
                # Create or get gallery
                if self.object.gallery:
                    gallery = self.object.gallery
                else:
                    gallery = Gallery.objects.create(name=f'Gallery-{self.object.pk}')
                    self.object.gallery = gallery
                    self.object.save(update_fields=['gallery'])
                
                # Save images
                images = image_formset.save(commit=False)
                for image in images:
                    if image.image:  # Only save if image is present
                        image.gallery = gallery
                        image.save()
                
                # Delete marked images
                for image in image_formset.deleted_objects:
                    image.delete()
        
        messages.success(self.request, f'Страница "{self.object.name}" успешно обновлена')
        return response
    
    def form_invalid(self, form, seo_form, gallery_form, image_formset):
        context = self.get_context_data()
        context['form'] = form
        context['seo_form'] = seo_form
        context['gallery_form'] = gallery_form
        context['image_formset'] = image_formset
        return self.render_to_response(context)


class PageElseDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = PageElse
    success_url = reverse_lazy('page:admin_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, можно ли удалять страницу
        page = self.get_object()
        if not page.can_delete:
            messages.error(request, f'Нельзя удалить страницу "{page.name}". Она является системной.')
            return redirect('page:admin_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        page_name = self.get_object().name
        messages.success(self.request, f'Страница "{page_name}" успешно удалена')
        return super().delete(request, *args, **kwargs)


# Views для PageContacts
class PageContactsUpdateView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = 'page/admin_contacts_form.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self):
        context = {}
        context['title'] = 'Редактировать страницу контактов'
        context['is_create'] = False
        context['show_language_switcher'] = False  # PageContacts has no multilingual fields
        
        # Get all contacts for formset
        contacts = PageContacts.objects.all()
        context['contacts_formset'] = ContactsFormSet(queryset=contacts)
        
        # Get SEO block from first contact (assuming shared SEO)
        first_contact = contacts.first() if contacts.exists() else None
        if first_contact and first_contact.seo_block:
            seo_block = first_contact.seo_block
        else:
            seo_block = SeoBlock()
        context['seo_form'] = SeoForm(instance=seo_block)
        
        return context
    
    def post(self, request, *args, **kwargs):
        contacts = PageContacts.objects.all()
        contacts_formset = ContactsFormSet(request.POST, request.FILES, queryset=contacts)
        
        # Get SEO form
        first_contact = contacts.first() if contacts.exists() else None
        if first_contact and first_contact.seo_block:
            seo_block = first_contact.seo_block
        else:
            seo_block = SeoBlock()
        seo_form = SeoForm(request.POST, instance=seo_block)
        
        if contacts_formset.is_valid() and seo_form.is_valid():
            return self.form_valid(contacts_formset, seo_form)
        else:
            return self.form_invalid(contacts_formset, seo_form)
    
    def form_valid(self, contacts_formset, seo_form):
        # Save contacts formset
        contacts_formset.save()
        
        # Save SEO form if it has data
        if seo_form.is_valid():
            has_seo_data = any([
                seo_form.cleaned_data.get('title'),
                seo_form.cleaned_data.get('keywords'),
                seo_form.cleaned_data.get('description'),
                seo_form.cleaned_data.get('url')
            ])
            
            if has_seo_data:
                seo_block = seo_form.save()
                # Link SEO block to first contact
                first_contact = PageContacts.objects.first()
                if first_contact:
                    first_contact.seo_block = seo_block
                    first_contact.save(update_fields=['seo_block'])
        
        messages.success(self.request, 'Страница контактов успешно обновлена')
        return redirect('page:admin_list')
    
    def form_invalid(self, contacts_formset, seo_form):
        context = self.get_context_data()
        context['contacts_formset'] = contacts_formset
        context['seo_form'] = seo_form
        return render(self.request, self.template_name, context)


