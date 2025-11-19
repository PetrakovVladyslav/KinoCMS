import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("DJANGO_SU_EMAIL", "admin1@example.com")
        password = os.environ.get("DJANGO_SU_PASSWORD", "ss7546")
        first_name = os.environ.get("DJANGO_SU_FIRST_NAME", "Admin1")
        last_name = os.environ.get("DJANGO_SU_LAST_NAME", "User1")

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, first_name=first_name, last_name=last_name, password=password)
            self.stdout.write(self.style.SUCCESS("Superuser created"))
        else:
            self.stdout.write("Superuser already exists")
