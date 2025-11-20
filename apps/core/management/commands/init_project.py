import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.cinema.enums import MovieFormat
from apps.cinema.models import Hall, Movie, Session
from apps.page.models import PageContacts, PageElse, PageMain


class Command(BaseCommand):
    help = "Create all system pages and records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=3,
        )

    def handle(self, *args, **options):
        self._create_superuser()
        self._create_system_pages()
        self._generate_sessions(options.get["days", 3])

        self.stdout.write(self.style.SUCCESS("\n✓ Все системные данные созданы!"))

    def _create_superuser(self):
        """Создает суперпользователя, если его не существует"""
        User = get_user_model()

        email = os.environ.get("DJANGO_SU_EMAIL", "admin1@example.com")
        password = os.environ.get("DJANGO_SU_PASSWORD", "ss7546")
        first_name = os.environ.get("DJANGO_SU_FIRST_NAME", "Admin1")
        last_name = os.environ.get("DJANGO_SU_LAST_NAME", "User1")

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, first_name=first_name, last_name=last_name, password=password)
            self.stdout.write("✓ Суперпользователь создан")
        else:
            self.stdout.write("✓ Суперпользователь уже существует")

    def _create_system_pages(self):
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

    def _generate_sessions(self, days_ahead=3):
        """Генерирует расписание сеансов на сегодня и следующие дни"""
        today = timezone.now().date()

        # Создаем список дат: сегодня + следующие N дней
        dates = [today + timedelta(days=i) for i in range(days_ahead + 1)]

        date_range_str = f"{today.strftime('%d.%m.%Y')} - {dates[-1].strftime('%d.%m.%Y')}"

        # Удаляем старые сеансы (все что раньше сегодняшнего дня)
        old_sessions_count = Session.objects.filter(start_time__date__lt=today).count()
        if old_sessions_count > 0:
            Session.objects.filter(start_time__date__lt=today).delete()
            self.stdout.write(self.style.WARNING(f"Удалено {old_sessions_count} устаревших сеансов"))

        # Получаем фильмы в прокате (start_date <= today)
        movies_in_theaters = Movie.objects.filter(start_date__lte=today)

        if not movies_in_theaters.exists():
            self.stdout.write(
                self.style.WARNING("Нет фильмов в прокате. Добавьте фильмы с датой начала проката <= сегодня.")
            )
            return

        # Получаем все залы
        halls = Hall.objects.select_related("cinema").all()

        if not halls.exists():
            self.stdout.write(self.style.WARNING("Нет залов в базе данных. Добавьте кинотеатры и залы."))
            return

        # Доступные форматы
        formats = [MovieFormat.TWO_D, MovieFormat.THREE_D, MovieFormat.IMAX]

        # Временные слоты для сеансов
        time_slots = [
            (10, 0),  # 10:00
            (12, 30),  # 12:30
            (15, 0),  # 15:00
            (17, 30),  # 17:30
            (20, 0),  # 20:00
            (22, 30),  # 22:30
        ]

        created_count = 0

        # Для каждой даты в диапазоне
        for date in dates:
            self.stdout.write(f"\n✓ Генерация сеансов на {date.strftime('%d.%m.%Y')}:")

            for hall in halls:
                # Выбираем случайный фильм
                movie = random.choice(movies_in_theaters)

                # Создаем 3-4 сеанса для этого зала
                num_sessions = random.randint(3, 4)

                # Выбираем случайные временные слоты без повторений
                selected_slots = random.sample(time_slots, num_sessions)

                for hour, minute in selected_slots:
                    # Создаем datetime для начала сеанса
                    start_time = timezone.make_aware(
                        datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))
                    )

                    # Длительность фильма: 1.5-3 часа
                    duration_hours = random.uniform(1.5, 3.0)
                    end_time = start_time + timedelta(hours=duration_hours)

                    # Случайная цена 80-120 грн
                    price = Decimal(random.randint(80, 120))

                    # Случайный формат
                    format_choice = random.choice(formats)

                    # Проверяем, не существует ли уже сеанс в это время в этом зале
                    if not Session.objects.filter(hall=hall, start_time=start_time).exists():
                        Session.objects.create(
                            movie=movie,
                            hall=hall,
                            start_time=start_time,
                            end_time=end_time,
                            price=price,
                            format=format_choice,
                        )
                        created_count += 1

                        self.stdout.write(
                            f"  Создан сеанс: {movie.name} в {hall.cinema.name} - {hall.name}, "
                            f"{start_time.strftime('%H:%M')}, {format_choice}, {price} грн"
                        )

        self.stdout.write(self.style.SUCCESS(f"\n✓ Успешно создано {created_count} сеансов на период {date_range_str}"))
