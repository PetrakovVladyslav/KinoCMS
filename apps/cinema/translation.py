from modeltranslation.translator import register, TranslationOptions
from .models import Movie, Cinema, Hall


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Cinema)
class CinemaTranslationOptions(TranslationOptions):
    fields = ("name", "description", "conditions")


@register(Hall)
class HallTranslationOptions(TranslationOptions):
    fields = ("name", "description")
