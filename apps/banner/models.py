from django.db import models

# Create your models here.


class BannerBackground(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="banner_background", null=True, blank=True)
    just_color = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class BannerSettings(models.Model):
    name = models.CharField(max_length=255)
    turn_speed = [('5', '5'),('10', '10'),('15', '15')]
    typeof_page = [('news', 'news'), ('promos', 'promos')]
    turning_speed = models.CharField(max_length=10, choices=turn_speed, default='5')
    turning_on = models.BooleanField(default=False)






#class Banner(models.Model):

