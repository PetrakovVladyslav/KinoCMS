from django.db import models

from apps.core.models import SeoBlock, Gallery


# Create your models here.

class PageContacts(models.Model):
    cinema_name = models.CharField(max_length=100)
    address = models.TextField()
    coordinates = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='page/logo', null=True, blank=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cinema_name
    
    def is_system_page(self):
        return True  # Страница контактов всегда системная


class PageMain(models.Model):
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    seo_text = models.TextField(blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Главная страница'
    
    def is_system_page(self):
        return True  # Главная страница всегда системная

class PageNewsSales(models.Model):
    TYPE_CHOICES = [
        ('news', 'Новость'),
        ('sale', 'Акция'),
    ]
    
    # Основная информация
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Тип')
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    # Даты
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    publish_date = models.DateField(null=True, blank=True, verbose_name='Дата публикации')
    
    # Медиа
    logo = models.ImageField(upload_to='page/logo', null=True, blank=True, verbose_name='Главная картинка')
    gallery = models.OneToOneField(Gallery, on_delete=models.CASCADE, blank=True, null=True)
    video_url = models.URLField(blank=True, verbose_name='Ссылка на видео')
    
    # SEO и статус
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField(default=False, verbose_name='Активна')
    
    class Meta:
        verbose_name = 'Новость/Акция'
        verbose_name_plural = 'Новости и Акции'
        ordering = ['-publish_date', '-date']
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"
    
    def is_news(self):
        return self.type == 'news'
    
    def is_sale(self):
        return self.type == 'sale'

class PageElse(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, verbose_name='Описание')
    logo = models.ImageField(upload_to='page/logo', null=True, blank=True)
    gallery = models.OneToOneField(Gallery, on_delete=models.CASCADE, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def is_system_page(self):
        # Системные страницы - это те, которые нельзя удалять
        return not self.can_delete



