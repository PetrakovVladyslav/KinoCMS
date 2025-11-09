import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.cinema.enums import MovieFormat
from apps.cinema.models import Hall, Movie, Session


class Command(BaseCommand):
    help = "Генерирует расписание сеансов на сегодня и завтра для фильмов в прокате"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить старые сеансы перед генерацией новых",
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

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

        # Для каждой даты (сегодня и завтра)
        for date in [today, tomorrow]:
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
                            f"Создан сеанс: {movie.name} в {hall.cinema.name} - {hall.name}, "
                            f"{start_time.strftime('%d.%m.%Y %H:%M')}, {format_choice}, {price} грн"
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nУспешно создано {created_count} сеансов на {today.strftime('%d.%m.%Y')} и {tomorrow.strftime('%d.%m.%Y')}"
            )
        )
