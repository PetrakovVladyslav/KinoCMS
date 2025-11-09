from modeltranslation.translator import register, TranslationOptions
from .models import PageMain, PageElse, PageNewsSales


@register(PageMain)
class PageMainTranslationOptions(TranslationOptions):
    fields = ("seo_text",)


@register(PageElse)
class PageElseTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(PageNewsSales)
class PageNewsSalesTranslationOptions(TranslationOptions):
    fields = ("name", "description")
