from django import forms
from .models import Movie
from .enums import MovieFormat

from apps.core.forms import (
    SeoBlockForm,
    ImageFormSet,
    FORM_CSS_CLASSES,
    PLACEHOLDERS,
    LABELS
)

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


