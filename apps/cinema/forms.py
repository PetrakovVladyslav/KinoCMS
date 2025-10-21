from django import forms
from .models import Movie, Cinema, SeoBlock1, Image1
from .enums import MovieFormat
from django.forms import modelformset_factory, inlineformset_factory

from apps.core.forms import (
    SeoBlockForm,
    ImageFormSet,
    FORM_CSS_CLASSES,
    PLACEHOLDERS,
    LABELS, ImageForm
)
from ..core.models import SeoBlock

DATE_INPUT_FORMAT = '%Y-%m-%d'

class PageMovieForm(forms.ModelForm):
    formats = forms.MultipleChoiceField(
        choices=MovieFormat.choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Форматы показа',
        help_text='Выберите один или несколько форматов показа фильма'
    )

    class Meta:
        model = Movie
        fields = ['title_ru', 'title_uk', 'description_ru', 'description_uk', 
                  'poster', 'trailer_url', 'start_date', 'end_date', 'formats', 'gallery', 'seo_block']

        widgets = {
            'title_ru': forms.TextInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'title_uk': forms.TextInput(attrs={
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
            'poster': forms.FileInput(attrs={
                'class': FORM_CSS_CLASSES['FILE_INPUT']
            }),
            'trailer_url': forms.URLInput(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT'],
                'placeholder': PLACEHOLDERS['TRAILER_URL']
            }),
            'start_date': forms.DateInput(format=DATE_INPUT_FORMAT, attrs={
                'class': FORM_CSS_CLASSES['DATE_INPUT'],
                'type': 'date',
                'style': 'max-width: 200px;'
            }),
            'end_date': forms.DateInput(format=DATE_INPUT_FORMAT, attrs={
                'class': FORM_CSS_CLASSES['DATE_INPUT'],
                'type': 'date',
                'style': 'max-width: 200px;'
            }),
            'gallery': forms.Select(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'seo_block': forms.Select(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
        }


        labels = {
            'title_ru': LABELS['TITLE_RU'],
            'title_uk': LABELS['TITLE_UK'],
            'description_ru': LABELS['DESCRIPTION_RU'],
            'description_uk': LABELS['DESCRIPTION_UK'],
            'poster': LABELS['POSTER'],
            'start_date': LABELS['START_DATE'],
            'end_date': LABELS['END_DATE'],
            'gallery': 'Галерея',
            'seo_block': 'SEO блок',
            'trailer_url': 'Ссылка на трейлер',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Устанавливаем формат для полей дат
        self.fields['start_date'].input_formats = [DATE_INPUT_FORMAT]
        self.fields['end_date'].input_formats = [DATE_INPUT_FORMAT]
        
        # Инициализируем поле форматов из instance
        if self.instance and self.instance.pk:
            self.initial['formats'] = self.instance.formats or []
            
        # Добавляем пустую опцию для select полей
        self.fields['gallery'].empty_label = "Выберите галерею (необязательно)"
        self.fields['seo_block'].empty_label = "Выберите SEO блок (необязательно)"

    def save(self, commit=True):
        # Стандартное сохранение без вмешательства в мультиязычные поля
        instance = super().save(commit=False)
            
        # Сохраняем выбранные форматы
        formats_data = self.cleaned_data.get('formats', [])
        instance.formats = list(formats_data)

        if commit:
            instance.save()
        return instance



class ImageForm1(forms.ModelForm):
    class Meta:
        model = Image1
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

GalleryImageFormSet = modelformset_factory(
    Image1,
    form=ImageForm1,
    extra=5,
    can_delete=True,
)


class CinemaForm(forms.ModelForm):
    class Meta:
        model = Cinema
        fields = ['name_ru', 'name_uk', 'description_ru', 'description_uk',
                  'conditions_ru', 'conditions_uk', 'logo', 'banner', 'gallery1', 'seo_block1']
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
            'conditions_ru': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 6
            }),
            'conditions_uk': forms.Textarea(attrs={
                'class': FORM_CSS_CLASSES['TEXTAREA'],
                'rows': 6
            }),
            'logo': forms.FileInput(attrs={
                'class': FORM_CSS_CLASSES['FILE_INPUT']
            }),
            'banner': forms.FileInput(attrs={
                'class': FORM_CSS_CLASSES['FILE_INPUT']
            }),
            'gallery1': forms.SelectMultiple(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
            'seo_block1': forms.Select(attrs={
                'class': FORM_CSS_CLASSES['TEXT_INPUT']
            }),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class SeoBlockForm1(forms.ModelForm):

    class Meta:
        model = SeoBlock1
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