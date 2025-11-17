from django.db import models

# Create your models here.


class BannerBackground(models.Model):
    title = models.CharField(max_length=255, default="Сквозной банер на заднем фоне")
    image = models.ImageField(upload_to="banner_background", null=True, blank=True)
    use_image = models.BooleanField(default=False)


class BannerSlider(models.Model):
    ROTATION_CHOICES = [
        (5, "5"),
        (10, "10"),
        (15, "15"),
    ]
    title = models.CharField(max_length=255, default="На главной верх")
    rotation_time = models.PositiveIntegerField(default=5, choices=ROTATION_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.rotation_time}s)"

    class Meta:
        verbose_name = "Верхний баннер"
        verbose_name_plural = "Верхние баннеры"


class BannerItem(models.Model):
    slider = models.ForeignKey(BannerSlider, on_delete=models.CASCADE, related_name="items")
    image = models.ImageField(upload_to="banner_image", null=True, blank=True)
    url = models.URLField(blank=True)
    text = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Banner Item {self.id}"

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Элемент верхнего баннера"
        verbose_name_plural = "Элементы верхнего баннера"


class BottomBannerSlider(models.Model):
    ROTATION_CHOICES = [
        (5, "5"),
        (10, "10"),
        (15, "15"),
    ]
    title = models.CharField(max_length=255, default="На главной Новости Акции внизу")
    rotation_time = models.PositiveIntegerField(default=5, choices=ROTATION_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.rotation_time}s)"

    class Meta:
        verbose_name = "Нижний баннер"
        verbose_name_plural = "Нижние баннеры"


class BottomBannerItem(models.Model):
    slider = models.ForeignKey(BottomBannerSlider, on_delete=models.CASCADE, related_name="items")
    image = models.ImageField(upload_to="banner_image", null=True, blank=True)
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Bottom Banner Item {self.id}"

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Элемент нижнего баннера"
        verbose_name_plural = "Элементы нижнего баннера"
