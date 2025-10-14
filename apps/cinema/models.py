from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from .enums import MovieFormat
from apps.core.models import Gallery, SeoBlock



# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name='Название фильма')
    description = models.TextField(blank=True, verbose_name='Описание фильма')
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    gallery = models.OneToOneField(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
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

    def __str__(self):
        return self.title



class Cinema(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название кинотеатра')
    description = models.TextField(blank=True, verbose_name='Описание')
    conditions = models.TextField(blank=True, verbose_name='Условия')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    banner = models.ImageField(upload_to='banners/', null=True, blank=True)
    gallery = models.OneToOneField(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Кинотеатры'
        verbose_name = 'Кинотеатр'

    def __str__(self):
        return self.name


class Hall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True,)
    scheme = models.ImageField(upload_to='schemes/', null=True, blank=True)
    banner = models.ImageField(upload_to='banners/', null=True, blank=True)
    gallery = models.OneToOneField(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Залы'
        verbose_name = 'Зал'
        unique_together = ['cinema', 'number']

    def __str__(self):
        return f"{self.cinema.name} - Зал {self.number}"


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='Фильм')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name='Зал')
    date = models.DateField(verbose_name='Дата сеанса')
    time = models.TimeField(verbose_name='Время сеанса')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    type3d = models.BooleanField(default=False)
    typeimax = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.movie.title} - {self.hall.cinema.name} Зал {self.hall.number} - {self.date} {self.time}'

    class Meta:
        verbose_name_plural = 'Сеансы'
        verbose_name = 'Сеанс'
        unique_together = ['hall', 'date', 'time']
        ordering = ['date', 'time']


