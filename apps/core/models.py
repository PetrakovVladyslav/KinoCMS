from django.db import models


# Create your models here.


class Gallery(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pk}"


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="gallery_images/", null=True, blank=True)


class SeoBlock(models.Model):
    title = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Title"
    )
    url = models.URLField(null=True, blank=True, verbose_name="URL")
    keywords = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Word"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    def __str__(self):
        return self.title or f"SEO block {self.id}"
