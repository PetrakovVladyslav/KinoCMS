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


class BannerItem(models.Model):
    slider = models.ForeignKey(BannerSlider, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="banner_image", null=True, blank=True)
    url = models.URLField(blank=True)
    text = models.TextField(blank=True)


class BottomBannerSlider(models.Model):
    ROTATION_CHOICES = [
        (5, "5"),
        (10, "10"),
        (15, "15"),
    ]
    title = models.CharField(max_length=255, default="На главной Новости Акции внизу")
    rotation_time = models.PositiveIntegerField(default=5, choices=ROTATION_CHOICES)
    is_active = models.BooleanField(default=True)


class BottomBannerItem(models.Model):
    slider = models.ForeignKey(BottomBannerSlider, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="banner_image", null=True, blank=True)
    url = models.URLField(blank=True)
