from modeltranslation.translator import TranslationOptions, register

from .models import Cinema, Hall, Movie


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Cinema)
class CinemaTranslationOptions(TranslationOptions):
    fields = ("name", "description", "conditions")


@register(Hall)
class HallTranslationOptions(TranslationOptions):
    fields = ("name", "description")
