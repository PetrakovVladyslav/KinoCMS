from django.core.management.base import BaseCommand
from apps.page.models import PageElse, PageMain, PageContacts


class Command(BaseCommand):
    help = "Create all system pages and records"

    def handle(self, *args, **options):
        # Обычные системные страницы
        system_pages_data = [
            {
                "slug": "about",
                "name": "О кинотеатре",
                "name_ru": "О кинотеатре",
                "name_uk": "Про кінотеатр",
                "description": "<p>Информация о нашем кинотеатре</p>",
                "description_ru": "<p>Информация о нашем кинотеатре</p>",
                "description_uk": "<p>Інформація про наш кінотеатр</p>",
            },
            {
                "slug": "cafe",
                "name": "Кафе-Бар",
                "name_ru": "Кафе-Бар",
                "name_uk": "Кафе-Бар",
                "description": "<p>Наше кафе и бар</p>",
                "description_ru": "<p>Наше кафе и бар</p>",
                "description_uk": "<p>Наше кафе та бар</p>",
            },
            {
                "slug": "vip",
                "name": "Vip-зал",
                "name_ru": "Vip-зал",
                "name_uk": "Vip-зал",
                "description": "<p>Наш vip-зал</p>",
                "description_ru": "<p>Наш vip-зал</p>",
                "description_uk": "<p>Наш vip-зал</p>",
            },
            {
                "slug": "promo",
                "name": "Реклама",
                "name_ru": "Реклама",
                "name_uk": "Реклама",
                "description": "<p>Рекламные возможности</p>",
                "description_ru": "<p>Рекламные возможности</p>",
                "description_uk": "<p>Рекламні можливості</p>",
            },
            {
                "slug": "kids_room",
                "name": "Детская комната",
                "name_ru": "Детская комната",
                "name_uk": "Дитяча кімната",
                "description": "<p>Детская комната</p>",
                "description_ru": "<p>Детская комната</p>",
                "description_uk": "<p>Дитяча кімната</p>",
            },
        ]

        for data in system_pages_data:
            page, created = PageElse.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "name_ru": data["name_ru"],
                    "name_uk": data["name_uk"],
                    "description": data["description"],
                    "description_ru": data["description_ru"],
                    "description_uk": data["description_uk"],
                    "status": True,
                    "is_system": True,
                },
            )
            if created:
                self.stdout.write(f"✓ Создана страница: {data['name']}")
            else:
                self.stdout.write(f"→ Страница уже существует: {data['name']}")

        # Главная страница (синглтон)
        if not PageMain.objects.exists():
            PageMain.objects.create(
                phone_number1="+380000000000",
                phone_number2="+380000000001",
                status=True,
                seo_text="Текст для SEO главной страницы...",
                can_delete=False,
            )
            self.stdout.write("✓ Создана главная страница")
        else:
            self.stdout.write("→ Главная страница уже существует")

        # Контакты - главный блок (обязательный)
        if not PageContacts.objects.filter(is_main=True).exists():
            PageContacts.objects.create(
                cinema_name="Главный кинотеатр",
                address="г. Киев, ул. Примерная, 1",
                coordinates="50.4504,30.5245",
                status=True,
                is_main=True,
                order=0,
            )
            self.stdout.write("✓ Создан главный блок контактов")
        else:
            self.stdout.write("→ Главный блок контактов уже существует")

        self.stdout.write(self.style.SUCCESS("Все системные страницы созданы!"))
