from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Gender(models.TextChoices):
    MALE = "male", _("мужской")
    FEMALE = "female", _("женский")


class Language(models.TextChoices):
    RUSSIAN = "ru", _("Русский")
    UKRAINIAN = "uk", _("Українська")


class City(models.TextChoices):
    KYIV = "kyiv", _("Киев")
    DNIPRO = "dnipro", _("Днепр")
    LVIV = "lviv", _("Львов")
    ODESA = "odessa", _("Одесса")
    KHARKIV = "kharkiv", _("Харьков")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Нужно ввести Email")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("is_staff must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superuser must have is_superuser=True")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    nickname = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=250)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=250, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    phone_number = models.CharField(max_length=10, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, choices=City.choices, blank=True, null=True)
    gender = models.CharField(
        max_length=100,
        choices=Gender.choices,
        blank=True,
        null=True,
        default=Gender.MALE,
    )
    language = models.CharField(
        max_length=100,
        choices=Language.choices,
        blank=True,
        null=True,
        default=Language.RUSSIAN,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def clean(self):
        text_fields = ["first_name", "last_name", "email", "address", "phone_number", "nickname"]
        for field in text_fields:
            value = getattr(self, field, None)
            if value:
                setattr(self, field, strip_tags(str(value)))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["nickname"], condition=models.Q(nickname__isnull=False), name="unique_nickname_when_not_null"
            ),
        ]
