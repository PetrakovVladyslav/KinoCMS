from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import PageContacts, PageNewsSales, PageMain, PageElse

# Register your models here.

@admin.register(PageContacts)
class PageContactsAdmin(admin.ModelAdmin):
    list_display = ['cinema_name', 'address', 'status', 'date']
    list_filter = ['status', 'date']
    search_fields = ['cinema_name', 'address']

@admin.register(PageNewsSales)
class PageNewsSalesAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'status', 'publish_date', 'date']
    list_filter = ['type', 'status', 'publish_date', 'date']
    search_fields = ['name', 'description']
    list_editable = ['status']
    ordering = ['-publish_date', '-date']
    
@admin.register(PageMain)
class PageMainAdmin(TranslationAdmin):
    list_display = ['phone_number1', 'phone_number2', 'status', 'date']
    list_filter = ['status', 'date']
    
@admin.register(PageElse)
class PageElseAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'can_delete', 'date']
    list_filter = ['status', 'can_delete', 'date']
    search_fields = ['name', 'description']
