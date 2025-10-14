from django import forms
from .models import Movie
from apps.core.models import Gallery, Image, SeoBlock
from django.forms import inlineformset_factory
from .enums import MovieFormat

# Константа для форматирования дат
DATE_INPUT_FORMAT = '%Y-%m-%d'


FORM_CSS_CLASSES = {
    'TEXT_INPUT': 'form-control',
    'TEXTAREA': 'form-control',
    'DATE_INPUT': 'form-control',
    'CHECKBOX': 'form-check-input',
    'FILE_INPUT': 'form-control-file',
    'CUSTOM_SWITCH': 'custom-control-input',
}

PLACEHOLDERS = {

    'PHONE_1': '+38 (099) 123-45-67',
    'PHONE_2': '+38 (099) 765-43-21',

    'TRAILER_URL': 'https://',

    # SEO
    'SEO_TITLE': 'Заголовок страницы для поисковых систем',
    'SEO_URL': 'https://',
    'SEO_KEYWORDS': 'ключевые, слова, через, запятую',
    'SEO_DESCRIPTION': 'Описание страницы для поисковых систем (до 160 символов)',
}

LABELS = {

    'TITLE_RU': 'Название фильма (русский)',
    'TITLE_UK': 'Название фильма (украинский)',
    'DESCRIPTION_RU': 'Описание (русский)',
    'DESCRIPTION_UK': 'Описание (украинский)',
    'POSTER': 'Постер',
    'START_DATE': 'Дата начала проката',
    'END_DATE': 'Дата окончания проката',


    'CAN_DELETE': 'Можно удалять',
    'IMAGE': 'Изображение',

    # SEO labels
    'META_TITLE': 'Title',
    'CANONICAL_URL': 'URL',
    'META_KEYWORDS': 'Keywords',
    'META_DESCRIPTION': 'Description'
}

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

ImageFormSet = inlineformset_factory(
    Gallery,
    Image,
    form=ImageForm,
    extra=5,
    max_num=10,
    can_delete=True
)