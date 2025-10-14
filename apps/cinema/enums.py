from django.db import models
from django.utils.translation import gettext_lazy as _


class MovieFormat(models.TextChoices):
    TWO_D = '2D', _('2D')
    THREE_D = '3D', _('3D')
    IMAX = 'IMAX', _('IMAX')