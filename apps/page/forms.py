from django import forms
from .models import PageMain, PageElse, PageContacts, PageNewsSales
from apps.core.forms import (
    SeoBlockForm,
    ImageFormSet,
    FORM_CSS_CLASSES,
    PLACEHOLDERS,
    LABELS
)


class PageMainForm(forms.ModelForm):

    class Meta:
        model = PageMain
        exclude = ['date', 'seo_block']

        widgets = {
            'phone_number1': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['PHONE_1']
            }),
            'phone_number2': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['PHONE_2']
            }),
            'status': forms.CheckboxInput(attrs={
                'class': FORM_CSS_CLASSES['CUSTOM_SWITCH'],
                'id': 'status-switch'
            }),
            'seo_text': forms.HiddenInput(),  # Скрываем базовое поле
            'seo_text_ru': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 4,
                'id': 'seo-text-ru'
            }),
            'seo_text_uk': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 4,
                'id': 'seo-text-uk'
            }),
        }

        labels = {
            'phone_number1': LABELS['PHONE_1'],
            'phone_number2': LABELS['PHONE_2'],
            'status': LABELS['STATUS'],
            'seo_text': LABELS['SEO_TEXT'],
            'seo_text_ru': LABELS['SEO_TEXT_RU'],
            'seo_text_uk': LABELS['SEO_TEXT_UK'],
        }

    def save(self, commit=True):
        #Синхронизация базового поля seo_text с мультиязычными полями
        instance = super().save(commit=False)
        
        # Обновляем базовое поле seo_text из мультиязычных полей
        if self.cleaned_data.get('seo_text_ru'):
            instance.seo_text = self.cleaned_data['seo_text_ru']
        elif self.cleaned_data.get('seo_text_uk'):
            instance.seo_text = self.cleaned_data['seo_text_uk']
        elif not instance.seo_text:  # Если все поля пустые
            instance.seo_text = ''  # Устанавливаем пустую строку
        
        if commit:
            instance.save()
        return instance


class PageElseForm(forms.ModelForm):

    class Meta:
        model = PageElse
        exclude = ['date', 'name', 'description', 'gallery', 'seo_block']

        widgets = {
            'name_ru': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'name_uk': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'description_ru': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 6
            }),
            'description_uk': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 6
            }),
            'logo': forms.FileInput(attrs={
                'class': FORM_CSS_CLASSES['FILE_INPUT']
            }),
            'status': forms.CheckboxInput(attrs={
                'class': FORM_CSS_CLASSES['CHECKBOX']
            }),
        }

        labels = {
            'name_ru': LABELS['NAME_RU'],
            'name_uk': LABELS['NAME_UK'],
            'description_ru': LABELS['DESCRIPTION_RU'],
            'description_uk': LABELS['DESCRIPTION_UK'],
            'logo': LABELS['LOGO'],
            'status': LABELS['STATUS'],
            'can_delete': LABELS['CAN_DELETE'],
        }

    def save(self, commit=True):
        #Синхронизация базовых полей с мультиязычными
        instance = super().save(commit=False)

        # Обновляем базовые поля из мультиязычных
        if self.cleaned_data.get('name_ru'):
            instance.name = self.cleaned_data['name_ru']
        elif self.cleaned_data.get('name_uk'):
            instance.name = self.cleaned_data['name_uk']

        if self.cleaned_data.get('description_ru'):
            instance.description = self.cleaned_data['description_ru']
        elif self.cleaned_data.get('description_uk'):
            instance.description = self.cleaned_data['description_uk']

        if commit:
            instance.save()
        return instance





class PageContactsForm(forms.ModelForm):

    class Meta:
        model = PageContacts
        exclude = ['date', 'seo_block']

        widgets = {
            'cinema_name': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['CINEMA_NAME']
            }),
            'address': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 4,
                'placeholder': PLACEHOLDERS['ADDRESS']
            }),
            'coordinates': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['COORDINATES']
            }),
            'logo': forms.FileInput(attrs={
                'class': FORM_CSS_CLASSES['FILE_INPUT']
            }),
            'status': forms.CheckboxInput(attrs={
                'class': FORM_CSS_CLASSES['CHECKBOX']
            }),
        }

        labels = {
            'cinema_name': LABELS['CINEMA_NAME'],
            'address': LABELS['ADDRESS'],
            'coordinates': LABELS['COORDINATES'],
            'logo': LABELS['LOGO'],
            'status': LABELS['ACTIVE'],
        }


class PageNewsSalesForm(forms.ModelForm):
    
    class Meta:
        model = PageNewsSales
        exclude = ['date', 'name', 'description', 'gallery', 'seo_block', 'type']
        
        widgets = {
            'name_ru': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'name_uk': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'description_ru': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 6
            }),
            'description_uk': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 6
            }),
            'publish_date': forms.DateInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'type': 'date'
            }),
            'video_url': forms.URLInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': FORM_CSS_CLASSES['CHECKBOX']
            }),
        }
        
        labels = {
            'name_ru': LABELS['NAME_RU'],
            'name_uk': LABELS['NAME_UK'],
            'description_ru': LABELS['DESCRIPTION_RU'],
            'description_uk': LABELS['DESCRIPTION_UK'],
            'publish_date': 'Дата публикации',
            'video_url': 'Ссылка на видео',
            'status': LABELS['STATUS'],
        }
    
    def save(self, commit=True):
        """Синхронизация базовых полей с мультиязычными"""
        instance = super().save(commit=False)
        
        # Обновляем базовые поля из мультиязычных
        if self.cleaned_data.get('name_ru'):
            instance.name = self.cleaned_data['name_ru']
        elif self.cleaned_data.get('name_uk'):
            instance.name = self.cleaned_data['name_uk']
        
        if self.cleaned_data.get('description_ru'):
            instance.description = self.cleaned_data['description_ru']
        elif self.cleaned_data.get('description_uk'):
            instance.description = self.cleaned_data['description_uk']
        
        if commit:
            instance.save()
        return instance

