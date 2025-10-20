from django import forms
from django.forms import inlineformset_factory
from .models import Gallery, Image, SeoBlock

FORM_CSS_CLASSES = {
    'TEXT_INPUT': 'form-control',
    'TEXTAREA': 'form-control',
    'DATE_INPUT': 'form-control',
    'CHECKBOX': 'form-check-input',
    'FILE_INPUT': 'form-control-file',
    'CUSTOM_SWITCH': 'custom-control-input',
}

DATE_INPUT_FORMAT = '%Y-%m-%d'


# === PLACEHOLDERS ===

PLACEHOLDERS = {
    'ADDRESS': 'Адрес кинотеатра',
    'CINEMA_NAME': 'Название кинотеатра',
    'COORDINATES': 'Координаты для карты',
    'DATE': '2025-10-15',
    'PHONE_1': '+38 (099) 123-45-67',
    'PHONE_2': '+38 (099) 765-43-21',
    'SEO_DESCRIPTION': 'Описание страницы для поисковых систем (до 160 символов)',
    'SEO_KEYWORDS': 'ключевые, слова, через, запятую',
    'SEO_TITLE': 'Заголовок страницы для поисковых систем',
    'SEO_URL': 'https://',
    'TRAILER_URL': 'https://',
    'URL': 'https://',
}


# === LABELS ===

LABELS = {
    # Общие
    'ACTIVE': 'Активный',
    'CAN_DELETE': 'Можно удалять',
    'DATE_S': 'Дата запуска акции',
    'IMAGE': 'Изображение',
    'LOGO': 'Логотип',
    'STATUS': 'Включена',

    # Контакты
    'ADDRESS': 'Адрес кинотеатра',
    'CINEMA_NAME': 'Название кинотеатра',
    'COORDINATES': 'Координаты для карты',

    # Фильмы
    'DESCRIPTION_RU': 'Описание (русский)',
    'DESCRIPTION_UK': 'Описание (украинский)',
    'END_DATE': 'Дата окончания проката',
    'POSTER': 'Постер',
    'START_DATE': 'Дата начала проката',
    'TITLE_RU': 'Название фильма (русский)',
    'TITLE_UK': 'Название фильма (украинский)',

    # Страницы
    'DESCRIPTION_RU': 'Описание (русский)',
    'DESCRIPTION_UK': 'Описание (украинский)',
    'NAME_RU': 'Название страницы (русский)',
    'NAME_UK': 'Название страницы (украинский)',
    'NAMES_RU': 'Название акции (русский)',
    'NAMES_UK': 'Название акции (украинский)',


    # Телефоны
    'PHONE_1': 'Телефон 1',
    'PHONE_2': 'Телефон 2',

    # SEO
    'CANONICAL_URL': 'URL',
    'META_DESCRIPTION': 'Description',
    'META_KEYWORDS': 'Keywords',
    'META_TITLE': 'Title',
    'SEO_TEXT': 'SEO текст',
    'SEO_TEXT_RU': 'SEO текст (русский)',
    'SEO_TEXT_UK': 'SEO текст (українська)',
    'URL': 'Ссылка на видео',
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
