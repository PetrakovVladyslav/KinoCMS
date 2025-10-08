from math import trunc

from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType



from config import settings

# Create your models here.

class Gallery(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Галереи'
        verbose_name = 'Галерея'

class Image(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery_images/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Изображения'
        verbose_name = 'Изображение'

    def __str__(self):
        return f"Изображение в {self.gallery.name}"


class SeoBlock(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Title')
    url = models.URLField(null=True, blank=True, verbose_name='URL')
    keywords = models.CharField(max_length=50, null=True, blank=True, verbose_name='Word')
    description = models.TextField(null=True, blank=True, verbose_name='Description')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'SEO блоки'
        verbose_name = 'SEO блок'


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('paid', 'Оплачено'),
    ]
    from apps.cinema.models import Session
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    session = models.ForeignKey('cinema.Session', on_delete=models.CASCADE, verbose_name='Сеанс')
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending', verbose_name='Статус')
    row = models.PositiveIntegerField(verbose_name='Ряд')
    seat_number = models.PositiveIntegerField(verbose_name='Номер места')
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена билета')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        
        verbose_name_plural = 'Бронирования'
        verbose_name = 'Бронирование'
        unique_together = ['session', 'row', 'seat_number']

    def __str__(self):
        return f'Бронь {self.user.username} - {self.session.movie.title} - Ряд {self.row} Место {self.seat_number}'
