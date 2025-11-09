from django import forms
from .models import Movie, Cinema, Hall
from .enums import MovieFormat

from apps.core.forms import (
    FORM_CSS_CLASSES,
    PLACEHOLDERS,
    LABELS,
)

DATE_INPUT_FORMAT = "%Y-%m-%d"


class PageMovieForm(forms.ModelForm):
    formats = forms.MultipleChoiceField(
        choices=MovieFormat.choices,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label="Форматы показа",
        help_text="Выберите один или несколько форматов показа фильма",
    )

    class Meta:
        model = Movie
        exclude = ["name", "description", "gallery", "seo_block"]

        widgets = {
            "name_ru": forms.TextInput(attrs={"class": FORM_CSS_CLASSES["TEXT_INPUT"]}),
            "name_uk": forms.TextInput(attrs={"class": FORM_CSS_CLASSES["TEXT_INPUT"]}),
            "description_ru": forms.Textarea(
                attrs={"class": FORM_CSS_CLASSES["TEXTAREA"], "rows": 6}
            ),
            "description_uk": forms.Textarea(
                attrs={"class": FORM_CSS_CLASSES["TEXTAREA"], "rows": 6}
            ),
            "poster": forms.FileInput(attrs={"class": FORM_CSS_CLASSES["FILE_INPUT"]}),
            "trailer_url": forms.URLInput(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXT_INPUT"],
                    "placeholder": PLACEHOLDERS["TRAILER_URL"],
                }
            ),
            "start_date": forms.DateInput(
                format=DATE_INPUT_FORMAT,
                attrs={
                    "class": FORM_CSS_CLASSES["DATE_INPUT"],
                    "type": "date",
                    "style": "max-width: 200px;",
                },
            ),
            "end_date": forms.DateInput(
                format=DATE_INPUT_FORMAT,
                attrs={
                    "class": FORM_CSS_CLASSES["DATE_INPUT"],
                    "type": "date",
                    "style": "max-width: 200px;",
                },
            ),
        }

        labels = {
            "name_ru": LABELS["TITLE_RU"],
            "name_uk": LABELS["TITLE_UK"],
            "description_ru": LABELS["DESCRIPTION_RU"],
            "description_uk": LABELS["DESCRIPTION_UK"],
            "poster": LABELS["POSTER"],
            "start_date": LABELS["START_DATE"],
            "end_date": LABELS["END_DATE"],
            "trailer_url": "Ссылка на трейлер",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["start_date"].input_formats = [DATE_INPUT_FORMAT]
        self.fields["end_date"].input_formats = [DATE_INPUT_FORMAT]

        if self.instance and self.instance.pk and self.instance.formats:
            self.initial["formats"] = self.instance.formats

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                {"end_date": "Дата окончания не может быть раньше даты начала"}
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Синхронизация базовых полей с мультиязычными
        if self.cleaned_data.get("name_ru"):
            instance.name = self.cleaned_data["name_ru"]
        elif self.cleaned_data.get("name_uk"):
            instance.name = self.cleaned_data["name_uk"]

        if self.cleaned_data.get("description_ru"):
            instance.description = self.cleaned_data["description_ru"]
        elif self.cleaned_data.get("description_uk"):
            instance.description = self.cleaned_data["description_uk"]

        # Обработка форматов
        formats_data = self.cleaned_data.get("formats", [])
        instance.formats = list(formats_data) if formats_data else []

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class CinemaForm(forms.ModelForm):
    class Meta:
        model = Cinema
        exclude = [
            "name",
            "description",
            "conditions",
            "gallery",
            "seo_block",
            "created_at",
        ]

        widgets = {
            "name_ru": forms.TextInput(attrs={"class": FORM_CSS_CLASSES["TEXT_INPUT"]}),
            "name_uk": forms.TextInput(attrs={"class": FORM_CSS_CLASSES["TEXT_INPUT"]}),
            "description_ru": forms.Textarea(
                attrs={"class": FORM_CSS_CLASSES["TEXTAREA"], "rows": 6}
            ),
            "description_uk": forms.Textarea(
                attrs={"class": FORM_CSS_CLASSES["TEXTAREA"], "rows": 6}
            ),
            "conditions_ru": forms.Textarea(
                attrs={"class": FORM_CSS_CLASSES["TEXTAREA"], "rows": 4}
            ),
            "conditions_uk": forms.Textarea(
                attrs={"class": FORM_CSS_CLASSES["TEXTAREA"], "rows": 4}
            ),
            "logo": forms.FileInput(attrs={"class": FORM_CSS_CLASSES["FILE_INPUT"]}),
            "banner": forms.FileInput(attrs={"class": FORM_CSS_CLASSES["FILE_INPUT"]}),
        }

        labels = {
            "name_ru": "Название кинотеатра (русский)",
            "name_uk": "Название кинотеатра (украинский)",
            "description_ru": LABELS["DESCRIPTION_RU"],
            "description_uk": LABELS["DESCRIPTION_UK"],
            "conditions_ru": "Условия (русский)",
            "conditions_uk": "Условия (украинский)",
            "logo": LABELS["LOGO"],
            "banner": "Баннер",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        exclude = [
            "name",
            "description",
            "gallery",
            "seo_block",
            "created_at",
            "cinema",
            "rows",
            "seats_per_row",
        ]

        widgets = {
            "name_ru": forms.TextInput(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXT_INPUT"],
                    "placeholder": "Название зала на русском",
                }
            ),
            "name_uk": forms.TextInput(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXT_INPUT"],
                    "placeholder": "Назва залу українською",
                }
            ),
            "description_ru": forms.Textarea(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXTAREA"],
                    "rows": 4,
                    "placeholder": "Описание зала на русском",
                }
            ),
            "description_uk": forms.Textarea(
                attrs={
                    "class": FORM_CSS_CLASSES["TEXTAREA"],
                    "rows": 4,
                    "placeholder": "Опис залу українською",
                }
            ),
            "banner": forms.FileInput(attrs={"class": FORM_CSS_CLASSES["FILE_INPUT"]}),
            "scheme_data": forms.HiddenInput(),
        }

        labels = {
            "name_ru": "Название зала (русский)",
            "name_uk": "Название зала (украинский)",
            "description_ru": "Описание (русский)",
            "description_uk": "Описание (украинский)",
            "banner": "Верхний баннер",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Синхронизация базовых полей с мультиязычными
        if self.cleaned_data.get("name_ru"):
            instance.name = self.cleaned_data["name_ru"]
        elif self.cleaned_data.get("name_uk"):
            instance.name = self.cleaned_data["name_uk"]

        if self.cleaned_data.get("description_ru"):
            instance.description = self.cleaned_data["description_ru"]
        elif self.cleaned_data.get("description_uk"):
            instance.description = self.cleaned_data["description_uk"]

        if commit:
            instance.save()
            self.save_m2m()

        return instance
