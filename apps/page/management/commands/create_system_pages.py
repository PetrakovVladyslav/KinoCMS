from django.core.management.base import BaseCommand

from apps.page.models import PageContacts, PageElse, PageMain


class Command(BaseCommand):
    help = "Create all system pages and records"

    def handle(self, *args, **options):
        # Обычные системные страницы
        system_pages_data = [
            {"slug": "about", "name": "О кинотеатре"},
            {"slug": "cafe", "name": "Кафе-Бар"},
            {"slug": "vip", "name": "Vip-зал"},
            {"slug": "promo", "name": "Реклама"},
            {"slug": "kids_room", "name": "Детская комната"},
        ]

        for data in system_pages_data:
            page, created = PageElse.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "is_system": True,
                    "status": True,
                    "description": f"<p>Содержимое страницы {data['name']}</p>",
                },
            )
            if created:
                self.stdout.write(f"✓ Создана страница: {data['name']}")

        # Главная страница
        if not PageMain.objects.exists():
            PageMain.objects.create(
                phone_number1="+380000000000",
                phone_number2="+380000000001",
                status=True,
                seo_text="Текст для SEO главной страницы...",
                can_delete=False,
            )
            self.stdout.write("✓ Создана главная страница")

        # Контакты - главный блок
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

        self.stdout.write(self.style.SUCCESS("Все системные страницы созданы!"))
