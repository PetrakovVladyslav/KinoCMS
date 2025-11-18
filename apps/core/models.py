import os

from django.db import models

# Create your models here.


class Gallery(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pk}"


class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="gallery_images/", null=False, blank=False)


class SeoBlock(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name="Title")  # обязательное поле
    url = models.URLField(null=False, blank=False, verbose_name="URL")  # обязательное поле
    keywords = models.CharField(max_length=255, null=False, blank=False, verbose_name="Keywords")  # обязательное поле
    description = models.TextField(null=False, blank=False, verbose_name="Description")  # обязательное поле

    def __str__(self):
        return self.title or f"SEO block {self.id}"


class MailingFile(models.Model):
    """Модель для хранения файлов, которые можно отправить в рассылке"""

    file = models.FileField(upload_to="mailing_files/", verbose_name="Файл")
    original_name = models.CharField(max_length=255, verbose_name="Название файла")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    file_size = models.IntegerField(default=0, verbose_name="Размер файла (байты)")

    class Meta:
        verbose_name = "Файл рассылки"
        verbose_name_plural = "Файлы рассылки"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        # Удаляем файл при удалении записи
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def get_file_size_display(self):
        """Возвращает размер файла в читаемом формате"""
        size = self.file_size
        for unit in ["Б", "КБ", "МБ", "ГБ"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"


class Mailing(models.Model):
    """Модель для хранения информации о рассылке"""

    STATUS_CHOICES = [
        ("pending", "В очереди"),
        ("processing", "Выполняется"),
        ("completed", "Завершена"),
        ("failed", "Ошибка"),
    ]

    file = models.ForeignKey(
        MailingFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Прикрепленный файл",
    )
    send_to_all = models.BooleanField(default=False, verbose_name="Отправить всем")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
    )
    total_recipients = models.IntegerField(default=0, verbose_name="Всего получателей")
    sent_count = models.IntegerField(default=0, verbose_name="Отправлено")
    failed_count = models.IntegerField(default=0, verbose_name="Ошибок")
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID задачи Celery",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Начата")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершена")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]

    def __str__(self):
        file_name = self.file.original_name if self.file else "Без файла"
        return f"Рассылка {self.id} - {file_name} ({self.get_status_display()})"

    def get_progress_percentage(self):
        """Возвращает процент выполнения рассылки"""
        if self.total_recipients == 0:
            return 0
        return int((self.sent_count + self.failed_count) / self.total_recipients * 100)


class MailingRecipient(models.Model):
    """Модель для хранения получателей конкретной рассылки"""

    STATUS_CHOICES = [
        ("pending", "Ожидает отправки"),
        ("sent", "Отправлено"),
        ("failed", "Ошибка"),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Рассылка",
    )
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Сообщение об ошибке",
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Отправлено")

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        unique_together = ["mailing", "user"]

    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()}"
