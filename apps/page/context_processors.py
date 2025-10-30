from .models import PageElse, PageMain


def page_context(request):
    """
    Добавляет информацию о страницах в контекст всех шаблонов
    """
    # Получаем все активные системные страницы с валидным slug
    system_pages = PageElse.objects.filter(is_system=True, status=True).exclude(slug='').order_by('name')
    
    # Получаем все активные пользовательские страницы с валидным slug
    custom_pages = PageElse.objects.filter(is_system=False, status=True).exclude(slug='').order_by('name')
    
    # Получаем главную страницу для телефонов
    page_main = PageMain.objects.filter(status=True).first()
    
    return {
        'system_pages': system_pages,
        'custom_pages': custom_pages,
        'page_main': page_main,
    }
