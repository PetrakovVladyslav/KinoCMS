from django import forms
from .models import PageMain, PageElse, PageContacts


class PageMainForm(forms.ModelForm):
    class Meta:
        model = PageMain
        exclude = ['date']  # Exclude date, seo_block will be handled separately
        widgets = {
            'phone_number1': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+38 (099) 123-45-67'
            }),
            'phone_number2': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+38 (099) 765-43-21'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'custom-control-input',
                'id': 'status-switch'
            }),
            'seo_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'id': 'seo-text-base'
            }),
            'seo_text_ru': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'id': 'seo-text-ru'
            }),
            'seo_text_uk': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'id': 'seo-text-uk'
            }),
        }
        labels = {
            'phone_number1': 'Телефон 1',
            'phone_number2': 'Телефон 2',
            'status': 'Включена',
            'seo_text': 'SEO текст',
            'seo_text_ru': 'SEO текст (русский)',
            'seo_text_uk': 'SEO текст (українська)',
        }


class PageElseForm(forms.ModelForm):
    class Meta:
        model = PageElse
        fields = '__all__'
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


class PageContactsForm(forms.ModelForm):
    class Meta:
        model = PageContacts
        fields = '__all__'
        widgets = {
            'cinema_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название кинотеатра'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Адрес кинотеатра'}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Координаты для карты'}),
            'logo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'cinema_name': 'Название кинотеатра',
            'address': 'Адрес кинотеатра',
            'coordinates': 'Координаты для карты',
            'logo': 'Логотип',
            'status': 'Активный',
        }
