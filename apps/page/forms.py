from django import forms
from django.forms import inlineformset_factory
from .models import PageMain, PageElse, PageContacts, PageNewsPromos
from apps.core.models import Gallery, Image, SeoBlock


# КОНСТАНТЫ ДЛЯ ФОРМ
DATE_INPUT_FORMAT = '%Y-%m-%d'

FORM_CSS_CLASSES = {
    'TEXT_INPUT': 'form-control',
    'TEXTAREA': 'form-control',
    'CHECKBOX': 'form-check-input',
    'FILE_INPUT': 'form-control-file',
    'CUSTOM_SWITCH': 'custom-control-input',
    'DATE_INPUT': 'form-control',

}

PLACEHOLDERS = {
    'URL': 'https://',
    'DATE': '2025-10-15',
    'PHONE_1': '+38 (099) 123-45-67',
    'PHONE_2': '+38 (099) 765-43-21',

    # Контакты
    'CINEMA_NAME': 'Название кинотеатра',
    'ADDRESS': 'Адрес кинотеатра',
    'COORDINATES': 'Координаты для карты',

    # SEO
    'SEO_TITLE': 'Заголовок страницы для поисковых систем',
    'SEO_URL': 'https://',
    'SEO_KEYWORDS': 'ключевые, слова, через, запятую',
    'SEO_DESCRIPTION': 'Описание страницы для поисковых систем (до 160 символов)',
}

LABELS = {
    # PageMain labels
    'PHONE_1': 'Телефон 1',
    'PHONE_2': 'Телефон 2',
    'STATUS': 'Включена',
    'SEO_TEXT': 'SEO текст',
    'SEO_TEXT_RU': 'SEO текст (русский)',
    'SEO_TEXT_UK': 'SEO текст (українська)',
    'DATE_S': 'Дата запуска акции',

    # PageElse labels
    'NAME_RU': 'Название страницы (русский)',
    'NAME_UK': 'Название страницы (украинский)',
    'DESCRIPTION_RU': 'Описание (русский)',
    'DESCRIPTION_UK': 'Описание (украинский)',
    'NAMES_RU': 'Название акции (русский)',
    'NAMES_UK': 'Название акции (украинский)',


    # PageContacts labels
    'CINEMA_NAME': 'Название кинотеатра',
    'ADDRESS': 'Адрес кинотеатра',
    'COORDINATES': 'Координаты для карты',
    'LOGO': 'Логотип',
    'ACTIVE': 'Активный',

    # Общие
    'CAN_DELETE': 'Можно удалять',
    'IMAGE': 'Изображение',

    # SEO labels
    'META_TITLE': 'Title',
    'CANONICAL_URL': 'URL',
    'META_KEYWORDS': 'Keywords',
    'META_DESCRIPTION': 'Description',
    'URL': 'Ссылка на видео'
}


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


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['image']

        widgets = {
            'image': forms.FileInput(attrs={
                'class': FORM_CSS_CLASSES['FILE_INPUT'],
                'accept': 'image/*'
            })
        }

        labels = {
            'image': LABELS['IMAGE'],
        }


class SeoBlockForm(forms.ModelForm):

    class Meta:
        model = SeoBlock
        fields = ['title', 'url', 'keywords', 'description']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['SEO_TITLE']
            }),
            'url': forms.URLInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['SEO_URL']
            }),
            'keywords': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['SEO_KEYWORDS']
            }),
            'description': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 3,
                'placeholder': PLACEHOLDERS['SEO_DESCRIPTION']
            }),
        }

        labels = {
            'title': LABELS['META_TITLE'],
            'url': LABELS['CANONICAL_URL'],
            'keywords': LABELS['META_KEYWORDS'],
            'description': LABELS['META_DESCRIPTION'],
        }


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



# Формсет для изображений галереи
ImageFormSet = inlineformset_factory(
    Gallery,
    Image,
    form=ImageForm,
    extra=5,
    max_num=10,
    can_delete=True
)

