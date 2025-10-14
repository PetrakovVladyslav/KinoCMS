from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import PageContacts, PageNewsPromos, PageMain, PageElse

# Register your models here.

@admin.register(PageContacts)
class PageContactsAdmin(admin.ModelAdmin):
    list_display = ['cinema_name', 'address', 'status', 'date']
    list_filter = ['status', 'date']
    search_fields = ['cinema_name', 'address']

@admin.register(PageNewsPromos)
class PageNewsPromosAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'date', 'url']
    list_filter = ['status', 'date']
    search_fields = ['name', 'description']
    
@admin.register(PageMain)
class PageMainAdmin(TranslationAdmin):
    list_display = ['phone_number1', 'phone_number2', 'status', 'date']
    list_filter = ['status', 'date']
    
@admin.register(PageElse)
class PageElseAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'can_delete', 'date']
    list_filter = ['status', 'can_delete', 'date']
    search_fields = ['name', 'description']
