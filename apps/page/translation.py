from modeltranslation.translator import register, TranslationOptions
from .models import PageMain, PageElse, PageContacts


@register(PageMain)
class PageMainTranslationOptions(TranslationOptions):
    fields = ('seo_text',)


@register(PageElse)
class PageElseTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


