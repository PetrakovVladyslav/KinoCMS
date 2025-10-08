from django import forms
from django.forms import modelformset_factory, HiddenInput
from .models import PageMain, PageElse, PageContacts
from apps.core.models import SeoBlock, Gallery, Image


class PageMainForm(forms.ModelForm):
    class Meta:
        model = PageMain
        fields = ['phone_number1', 'phone_number2', 'status', 'seo_text_ru', 'seo_text_uk']
        widgets = {
            'phone_number1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0994718721'}),
            'phone_number2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0994718722'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seo_text_ru': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'seo_text_uk': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'phone_number1': 'Телефон 1',
            'phone_number2': 'Телефон 2', 
            'status': 'Включена',
            'seo_text_ru': 'SEO текст (русский)',
            'seo_text_uk': 'SEO текст (українська)',
        }


class PageElseForm(forms.ModelForm):
    class Meta:
        model = PageElse
        fields = ['name_ru', 'name_uk', 'description_ru', 'description_uk', 'logo', 'status']
        widgets = {
            'name_ru': forms.TextInput(attrs={'class': 'form-control'}),
            'name_uk': forms.TextInput(attrs={'class': 'form-control'}),
            'description_ru': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'description_uk': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'logo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name_ru': 'Название страницы (русский)',
            'name_uk': 'Название страницы (украинский)',
            'description_ru': 'Описание (русский)',
            'description_uk': 'Описание (украинский)',
            'logo': 'Логотип',
            'status': 'Включена',
        }


class ContactsForm(forms.ModelForm):
    cinema_name = forms.CharField(
        max_length=50, 
        label='Название кинотеатра', 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Название кинотеатра'
        })
    )
    address = forms.CharField(
        label='Адрес кинотеатра', 
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': '4', 
            'placeholder': 'Адрес кинотеатра'
        })
    )
    coordinates = forms.CharField(
        label='Координаты для карты', 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Координаты для карты'
        })
    )
    status = forms.BooleanField(
        required=False, 
        label='Активный',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = PageContacts
        fields = ['cinema_name', 'address', 'coordinates', 'logo', 'status']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'logo': 'Логотип',
        }


# Contacts formset
ContactsFormSet = modelformset_factory(
    PageContacts,
    ContactsForm,
    fields=('cinema_name', 'address', 'coordinates', 'logo', 'status'),
    extra=1,  # Allow one extra form for adding new contacts
    can_delete=True,
    max_num=10  # Limit maximum number of contacts
)
ContactsFormSet.deletion_widget = HiddenInput


# SEO Block Form
class SeoForm(forms.ModelForm):
    title = forms.CharField(
        required=False, 
        max_length=200, 
        label='SEO Title', 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'SEO заголовок'
        })
    )
    keywords = forms.CharField(
        required=False, 
        max_length=400, 
        label='Ключевые слова',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ключевые слова, через, запятую'
        })
    )
    description = forms.CharField(
        required=False, 
        max_length=400, 
        label='Описание',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'SEO описание'
        })
    )
    url = forms.URLField(
        required=False, 
        label='URL', 
        widget=forms.URLInput(attrs={
            'class': 'form-control', 
            'placeholder': 'https://example.com'
        })
    )

    class Meta:
        model = SeoBlock
        fields = ['url', 'title', 'keywords', 'description']


# Gallery Form 
class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Название галереи'
            }),
        }
        labels = {
            'name': 'Название галереи',
        }


# Image Form for Gallery
class ImageForm(forms.ModelForm):
    image = forms.ImageField(
        required=False, 
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        }), 
        label=''
    )

    class Meta:
        model = Image
        fields = ['image']


# Image Formset
ImageInlineFormset = modelformset_factory(
    Image, 
    ImageForm, 
    fields=('image',), 
    extra=5,
    can_delete=True
)
ImageInlineFormset.deletion_widget = HiddenInput
