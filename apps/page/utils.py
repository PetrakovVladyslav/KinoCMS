
from typing import Optional, List, Dict
from apps.core.models import Gallery, SeoBlock



SEO_DEFAULTS = {
    'SITE_NAME': 'Кинотеатр',
    'MAIN_PAGE_TITLE': 'Главная страница - Кинотеатр',
    'MAIN_PAGE_DESC': 'Главная страница кинотеатра',
    'CONTACTS_TITLE': 'Контакты - Кинотеатр',
    'CONTACTS_DESC': 'Контакты и адреса кинотеатра',
}



DEFAULT_MAIN_PAGE_DATA = {
    'phone_number1': '',
    'phone_number2': '',
    'seo_text': '',
    'status': True
}

DEFAULT_CONTACT_DATA = {
    'cinema_name': 'Кинотеатр',
    'address': 'ул. Пример, 1',
    'coordinates': '',
    'status': True
}

# Конфигурация системных страниц
SYSTEM_PAGES_CONFIG: List[Dict[str, str]] = [
    {
        'name': 'О кинотеатре',
        'name_ru': 'О кинотеатре',
        'name_uk': 'Про кінотеатр',
        'template_title': 'Редактировать страницу "О кинотеатре"'
    },
    {
        'name': 'Кафе-бар',
        'name_ru': 'Кафе-бар',
        'name_uk': 'Кафе-бар',
        'template_title': 'Редактировать страницу "Кафе-бар"'
    },
    {
        'name': 'VIP-зал',
        'name_ru': 'VIP-зал',
        'name_uk': 'VIP-зал',
        'template_title': 'Редактировать страницу "VIP-зал"'
    },
    {
        'name': 'Реклама',
        'name_ru': 'Реклама',
        'name_uk': 'Реклама',
        'template_title': 'Редактировать страницу "Реклама"'
    },
    {
        'name': 'Детская комната',
        'name_ru': 'Детская комната',
        'name_uk': 'Дитяча кімната',
        'template_title': 'Редактировать страницу "Детская комната"'
    },
]



def ensure_gallery_for_page(page) -> Gallery:

   # Создает галерею для страницы, если её нет.

    if not page.gallery:
        gallery = Gallery.objects.create(name=f'Галерея - {page.name}')
        page.gallery = gallery
        page.save()
    return page.gallery


def ensure_seo_block(page_instance, title: str, description: str) -> SeoBlock:

    if not page_instance.seo_block:
        seo_block = SeoBlock.objects.create(
            title=title,
            description=description
        )
        page_instance.seo_block = seo_block
        page_instance.save()
    return page_instance.seo_block


def ensure_seo_block_for_page(page) -> SeoBlock:

    title = f'{page.name} - {SEO_DEFAULTS["SITE_NAME"]}'
    description = f'Страница {page.name} кинотеатра'
    return ensure_seo_block(page, title, description)


def ensure_seo_block_for_main_page(main_page) -> SeoBlock:

    return ensure_seo_block(
        main_page,
        SEO_DEFAULTS['MAIN_PAGE_TITLE'],
        SEO_DEFAULTS['MAIN_PAGE_DESC']
    )


def ensure_seo_block_for_contacts_page() -> SeoBlock:

    # Получаем или создаем главный контакт
    main_contact = get_or_create_main_contact()

    return ensure_seo_block(
        main_contact,
        SEO_DEFAULTS['CONTACTS_TITLE'],
        SEO_DEFAULTS['CONTACTS_DESC']
    )



def get_or_create_main_contact():

    #Получает или создает главный контакт кинотеатра.

    from .models import PageContacts

    main_contact = PageContacts.objects.first()
    if not main_contact:
        main_contact = PageContacts.objects.create(**DEFAULT_CONTACT_DATA)
    return main_contact


def get_or_create_main_page():

    from .models import PageMain


    main_page = PageMain.objects.first()
    if not main_page:
        main_page = PageMain.objects.create(**DEFAULT_MAIN_PAGE_DATA)
    return main_page


def ensure_system_pages():
    from .models import PageElse
    
    # Проверяем, есть ли уже все системные страницы
    existing_pages = set(PageElse.objects.filter(
        name__in=[config['name'] for config in SYSTEM_PAGES_CONFIG],
        can_delete=False
    ).values_list('name', flat=True))
    
    required_pages = set(config['name'] for config in SYSTEM_PAGES_CONFIG)
    
    # Создаем только недостающие страницы
    missing_pages = required_pages - existing_pages
    
    if missing_pages:
        for config in SYSTEM_PAGES_CONFIG:
            if config['name'] in missing_pages:
                PageElse.objects.get_or_create(
                    name=config['name'],
                    defaults={
                        'name_ru': config['name_ru'],
                        'name_uk': config['name_uk'],
                        'description': '',
                        'can_delete': False,
                        'status': True
                    }
                )

def get_system_page_config(page_name: str) -> Optional[Dict[str, str]]:

    #Получает конфигурацию системной страницы по её имени.

    for config in SYSTEM_PAGES_CONFIG:
        if config['name'] == page_name:
            return config
    return None