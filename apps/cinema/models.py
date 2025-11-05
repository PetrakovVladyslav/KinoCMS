from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.fields import  GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .enums import MovieFormat
from apps.core.models import Gallery, SeoBlock



# Create your models here.

class Movie(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название фильма')
    description = models.TextField(blank=True, verbose_name='Описание фильма')
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    trailer_url = models.URLField(null=True, blank=True, verbose_name='Ссылка на трейлер')
    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала проката')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания проката')
    formats = ArrayField(
        models.CharField(max_length=10, choices=MovieFormat.choices),
        default=list,
        blank=True,
        verbose_name='Форматы показа'
    )
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Фильмы'
        verbose_name = 'Фильм'

    def get_gallery_images(self):
        """Возвращает все изображения из галереи фильма"""
        if self.gallery:
            return self.gallery.images.all()
        return []
    
    def __str__(self):
        return self.name


class Cinema(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название кинотеатра')
    description = models.TextField(blank=True, verbose_name='Описание')
    conditions = models.TextField(blank=True, verbose_name='Условия')
    logo = models.ImageField(upload_to='cinema/logos/', null=True, blank=True)
    banner = models.ImageField(upload_to='cinema/banners/', null=True, blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Кинотеатры'
        verbose_name = 'Кинотеатр'

    def get_gallery_images(self):
        """Возвращает все изображения из галереи кинотеатра"""
        if self.gallery:
            return self.gallery.images.all()
        return []

    def __str__(self):
        return self.name


class Hall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='halls')
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True,)
    banner = models.ImageField(upload_to='banners/', null=True, blank=True)
    scheme_data = models.JSONField(null=True, blank=True, verbose_name='Схема зала')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name_plural = 'Залы'
        verbose_name = 'Зал'
        unique_together = ['cinema', 'name']
    
    def get_gallery_images(self):
        """Возвращает все изображения из галереи зала"""
        if self.gallery:
            return self.gallery.images.all()
        return []

    def __str__(self):
        return f"{self.cinema.name} - Зал {self.name}"


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='Фильм')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name='Зал')
    start_time = models.DateTimeField(verbose_name='Начало сеанса', default=timezone.now)
    end_time = models.DateTimeField(verbose_name='Окончание сеанса', default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    format = models.CharField(
        max_length=10, 
        choices=MovieFormat.choices,
        default=MovieFormat.TWO_D,
        verbose_name='Формат'
    )

    def __str__(self):
        return f'{self.movie.name} - {self.start_time.strftime("%Y/%m/%d")}'

    class Meta:
        verbose_name_plural = 'Сеансы'
        verbose_name = 'Сеанс'


class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    row = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['hall', 'number', 'row']
        ordering = ['number', 'row']

    def __str__(self):
        return f'Ряд {self.row},  место {self.number}'

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='Сеанс')
    seats = models.ManyToManyField(Seat)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена билета')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Действительна до')
    is_paid = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'


    def save(self, *args, **kwargs):
        # если не указано время истечения — ставим 15 минут
        if not self.expires_at and not self.is_paid:
            self.expires_at = timezone.now() + timedelta(minutes=15)

        # Обновляем total_amount только если объект уже сохранен (есть ID) и места добавлены
        if self.pk and self.ticket_price and self.seats.exists():
            self.total_amount = self.ticket_price * self.seats.count()

        super().save(*args, **kwargs)

    def is_expired(self):
        return not self.is_paid and timezone.now() > self.expires_at

    def __str__(self):
        return f'Бронь №{self.id} — {self.user or "Гость"}'