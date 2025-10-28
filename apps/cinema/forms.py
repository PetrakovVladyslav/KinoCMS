from django import forms
from .models import Movie, Cinema
from apps.core.models import Gallery, SeoBlock
from .enums import MovieFormat
from django.forms import modelformset_factory, inlineformset_factory

from apps.core.forms import (
    FORM_CSS_CLASSES,
    PLACEHOLDERS,
    LABELS,
)
from ..core.models import SeoBlock, Gallery

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
        fields = ['name_ru', 'name_uk', 'description_ru', 'description_uk',
                  'poster', 'trailer_url', 'start_date', 'end_date', 'formats',]

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
            'poster': forms.ClearableFileInput(attrs={
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
        }

        labels = {
            'name_ru': LABELS['NAME_RU'],
            'name_uk': LABELS['NAME_UK'],
            'description_ru': LABELS['DESCRIPTION_RU'],
            'description_uk': LABELS['DESCRIPTION_UK'],
            'poster': LABELS['POSTER'],
            'start_date': LABELS['START_DATE'],
            'end_date': LABELS['END_DATE'],
            'trailer_url': 'Ссылка на трейлер',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].input_formats = [DATE_INPUT_FORMAT]
        self.fields['end_date'].input_formats = [DATE_INPUT_FORMAT]

        if self.instance and self.instance.pk and self.instance.formats:
            self.initial['formats'] = self.instance.formats

        if self.instance and self.instance.poster:
            from django.utils.safestring import mark_safe
            self.fields['poster'].help_text = mark_safe(
                f'<div class="mt-2">'
                f'<img src="{self.instance.poster.url}" '
                f'alt="Текущий постер" '
                f'class="img-thumbnail" '
                f'style="max-width: 200px; max-height: 300px; object-fit: cover;">'
                f'</div>'
            )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError({
                'end_date': 'Дата окончания не может быть раньше даты начала'
            })

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        formats_data = self.cleaned_data.get('formats', [])
        instance.formats = list(formats_data) if formats_data else []

        if commit:
            instance.save()
            self.save_m2m()

        return instance