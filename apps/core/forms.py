from django import forms
from django.forms import inlineformset_factory
from .models import Gallery, GalleryImage, SeoBlock
from django.forms import BaseInlineFormSet

FORM_CSS_CLASSES = {
    "TEXT_INPUT": "form-control",
    "TEXTAREA": "form-control",
    "DATE_INPUT": "form-control",
    "CHECKBOX": "form-check-input",
    "FILE_INPUT": "form-control-file",
    "CUSTOM_SWITCH": "custom-control-input",
}

DATE_INPUT_FORMAT = "%Y-%m-%d"


# === PLACEHOLDERS ===

PLACEHOLDERS = {
    "ADDRESS": "Адрес кинотеатра",
    "CINEMA_NAME": "Название кинотеатра",
    "COORDINATES": "Координаты для карты",
    "DATE": "2025-10-15",
    "PHONE_1": "+38 (099) 123-45-67",
    "PHONE_2": "+38 (099) 765-43-21",
    "SEO_DESCRIPTION": "Описание страницы для поисковых систем (до 160 символов)",
    "SEO_KEYWORDS": "ключевые, слова, через, запятую",
    "SEO_TITLE": "Заголовок страницы для поисковых систем",
    "SEO_URL": "https://",
    "TRAILER_URL": "https://",
    "URL": "https://",
}


# === LABELS ===

LABELS = {
    # Общие
    "ACTIVE": "Активный",
    "CAN_DELETE": "Можно удалять",
    "DATE_S": "Дата запуска акции",
    "IMAGE": "Изображение",
    "LOGO": "Логотип",
    "STATUS": "Включена",
    # Контакты
    "ADDRESS": "Адрес кинотеатра",
    "CINEMA_NAME": "Название кинотеатра",
    "COORDINATES": "Координаты для карты",
    # Фильмы
    "MOVIE_NAME_RU": "Описание (русский)",
    "MOVIE_DESCRIPTION_UK": "Описание (украинский)",
    "END_DATE": "Дата окончания проката",
    "POSTER": "Постер",
    "START_DATE": "Дата начала проката",
    "TITLE_RU": "Название фильма (русский)",
    "TITLE_UK": "Название фильма (украинский)",
    # Страницы
    "DESCRIPTION_RU": "Описание (русский)",
    "DESCRIPTION_UK": "Описание (украинский)",
    "NAME_RU": "Название страницы (русский)",
    "NAME_UK": "Название страницы (украинский)",
    "NAMES_RU": "Название акции (русский)",
    "NAMES_UK": "Название акции (украинский)",
    # Телефоны
    "PHONE_1": "Телефон 1",
    "PHONE_2": "Телефон 2",
    # SEO
    "CANONICAL_URL": "URL",
    "META_DESCRIPTION": "Description",
    "META_KEYWORDS": "Keywords",
    "META_TITLE": "Title",
    "SEO_TEXT": "SEO текст",
    "SEO_TEXT_RU": "SEO текст (русский)",
    "SEO_TEXT_UK": "SEO текст (українська)",
    "URL": "Ссылка на видео",
}


class SeoBlockForm(forms.ModelForm):
    class Meta:
        model = SeoBlock
        fields = ["title", "url", "keywords", "description"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXT_INPUT"],
                    "placeholder": PLACEHOLDERS["SEO_TITLE"],
                }
            ),
            "url": forms.URLInput(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXT_INPUT"],
                    "placeholder": PLACEHOLDERS["SEO_URL"],
                }
            ),
            "keywords": forms.TextInput(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXT_INPUT"],
                    "placeholder": PLACEHOLDERS["SEO_KEYWORDS"],
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXTAREA"],
                    "rows": 3,
                    "placeholder": PLACEHOLDERS["SEO_DESCRIPTION"],
                }
            ),
        }

        labels = {
            "title": LABELS["META_TITLE"],
            "url": LABELS["CANONICAL_URL"],
            "keywords": LABELS["META_KEYWORDS"],
            "description": LABELS["META_DESCRIPTION"],
        }


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["image"]

        widgets = {
            "image": forms.FileInput(
                attrs={"class": FORM_CSS_CLASSES["FILE_INPUT"], "accept": "image/*"}
            )
        }

        labels = {
            "image": LABELS["IMAGE"],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.image:
            self.fields["image"].widget.attrs.update(
                {"data-current-image": self.instance.image.url}
            )

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if image and hasattr(image, "content_type"):  # Проверка что это новый файл
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Размер изображения не должен превышать 5MB"
                )

            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Поддерживаются только форматы: JPEG, PNG, WebP"
                )

        return image


class BaseGalleryFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        images_count = 0

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE", False):
                continue

            # Считаем существующие и новые изображения
            if form.cleaned_data.get("image"):
                images_count += 1

        if images_count == 0:
            raise forms.ValidationError("Загрузите хотя бы одно изображение")


GalleryFormSet = inlineformset_factory(
    Gallery,
    GalleryImage,
    form=GalleryImageForm,
    formset=BaseGalleryFormSet,
    extra=5,
    max_num=10,
    can_delete=True,
    validate_max=True,
)
