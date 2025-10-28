from .models import PageElse, PageMain


def page_context(request):
    """
    Добавляет информацию о страницах в контекст всех шаблонов
    """
    # Получаем все активные системные страницы
    system_pages = PageElse.objects.filter(is_system=True, status=True).order_by('name')
    
    # Получаем все активные пользовательские страницы
    custom_pages = PageElse.objects.filter(is_system=False, status=True).order_by('name')
    
    # Получаем главную страницу для телефонов
    page_main = PageMain.objects.filter(status=True).first()
    
    return {
        'system_pages': system_pages,
        'custom_pages': custom_pages,
        'page_main': page_main,
    }
