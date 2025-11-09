from django.db import models
from django.utils.text import slugify
from transliterate import translit

from apps.core.models import Gallery, SeoBlock

# Create your models here.


class PageContacts(models.Model):
    cinema_name = models.CharField(max_length=100)
    address = models.TextField()
    coordinates = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="page/logo", null=True, blank=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)
    is_main = models.BooleanField(default=False, verbose_name="Главный блок")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    status = models.BooleanField(default=True, verbose_name="Активен")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Блок контактов"
        verbose_name_plural = "Блоки контактов"

    def __str__(self):
        prefix = "[Главный] " if self.is_main else ""
        return f"{prefix}{self.cinema_name}"

    @property
    def can_delete(self):
        """Главный блок нельзя удалить"""
        return not self.is_main

    def save(self, *args, **kwargs):
        if self.is_main:
            # Снимаем флаг is_main с других блоков
            PageContacts.objects.filter(is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)


class PageMain(models.Model):
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    seo_text = models.TextField(blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return "Главная страница"


class PageNewsSales(models.Model):
    TYPE_CHOICES = [
        ("news", "Новость"),
        ("sale", "Акция"),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Тип")
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    publish_date = models.DateField(null=True, blank=True, verbose_name="Дата публикации")

    logo = models.ImageField(upload_to="page/logo", null=True, blank=True, verbose_name="Главная картинка")
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    video_url = models.URLField(blank=True, verbose_name="Ссылка на видео")

    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField(default=False, verbose_name="Активна")

    class Meta:
        verbose_name = "Новость/Акция"
        verbose_name_plural = "Новости и Акции"
        ordering = ["-publish_date", "-date"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

    def is_news(self):
        return self.type == "news"

    def is_sale(self):
        return self.type == "sale"


class PageElse(models.Model):
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, verbose_name="Описание")
    logo = models.ImageField(upload_to="page/logo", null=True, blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Генерируем slug из названия
            try:
                # Пробуем транслитерировать с русского/украинского на латиницу
                base_slug = translit(self.name, "ru", reversed=True)
            except Exception:
                # Если не получилось, используем название как есть
                base_slug = self.name

            base_slug = slugify(base_slug)
            slug = base_slug
            counter = 1

            # Проверяем уникальность slug
            while PageElse.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
