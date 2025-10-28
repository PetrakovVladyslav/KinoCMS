from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Описание команды'

    def add_arguments(self, parser):
        # Добавьте аргументы командной строки если нужно
        parser.add_argument(
            '--option',
            type=str,
            help='Пример опции',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Команда выполнена успешно!'))
