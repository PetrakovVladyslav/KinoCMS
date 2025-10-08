from modeltranslation.translator import register, TranslationOptions
from .models import PageMain, PageElse, PageContacts


@register(PageMain)
class PageMainTranslationOptions(TranslationOptions):
    fields = ('seo_text',)


@register(PageElse)
class PageElseTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


# PageContacts - no multilingual fields needed
# SeoBlock - no multilingual fields needed  
# Gallery - no multilingual fields needed
