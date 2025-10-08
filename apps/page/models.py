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

class PageNewsPromos(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    logo = models.ImageField(upload_to='page/logo', null=True, blank=True)
    status = models.BooleanField(default=False)
    url = models.URLField()
    gallery = models.OneToOneField(Gallery, on_delete=models.CASCADE, blank=True, null=True)
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class PageMain(models.Model):
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    seo_text = models.TextField()
    seo_block = models.OneToOneField(SeoBlock, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Главная страница'
    
    def is_system_page(self):
        return True  # Главная страница всегда системная

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



