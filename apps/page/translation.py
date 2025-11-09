from modeltranslation.translator import TranslationOptions, register

from .models import PageElse, PageMain, PageNewsSales


@register(PageMain)
class PageMainTranslationOptions(TranslationOptions):
    fields = ("seo_text",)


@register(PageElse)
class PageElseTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(PageNewsSales)
class PageNewsSalesTranslationOptions(TranslationOptions):
    fields = ("name", "description")
