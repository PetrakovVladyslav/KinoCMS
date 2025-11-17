"""Celery tasks для рассылок"""

import logging
import time

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from apps.core.models import Mailing, MailingRecipient

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def send_mailing_task(self, mailing_id):
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        mailing.status = "processing"
        mailing.started_at = timezone.now()
        mailing.celery_task_id = self.request.id
        mailing.save()

        recipients = MailingRecipient.objects.filter(mailing=mailing, status="pending").select_related("user")

        total = recipients.count()

        if total == 0:
            mailing.status = "completed"
            mailing.completed_at = timezone.now()
            mailing.save()
            return {"status": "completed", "sent_count": 0, "failed_count": 0}

        sent_count = 0
        failed_count = 0

        delay = 0.5

        for i, recipient in enumerate(recipients, 1):
            try:
                # Отправляем email с вложением
                email = EmailMessage(
                    subject="Файл от KinoCMS",
                    body="Здравствуйте! Отправляем вам файл.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient.user.email],
                )

                # Прикрепляем файл, если он есть
                if mailing.file and mailing.file.file:
                    email.attach_file(mailing.file.file.path)

                email.send(fail_silently=False)

                # Обновляем статус получателя
                recipient.status = "sent"
                recipient.sent_at = timezone.now()
                recipient.save(update_fields=["status", "sent_at"])

                sent_count += 1

            except Exception as e:
                # В случае ошибки отмечаем получателя
                recipient.status = "failed"
                recipient.error_message = str(e)[:500]  # Ограничиваем длину
                recipient.save(update_fields=["status", "error_message"])

                failed_count += 1

            # Обновляем прогресс рассылки в БД
            mailing.sent_count = sent_count
            mailing.failed_count = failed_count
            mailing.save(update_fields=["sent_count", "failed_count"])

            # Обновляем Celery State для real-time прогресс-бара
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i,
                    "total": total,
                    "percent": int((i / total) * 100),
                    "sent": sent_count,
                    "failed": failed_count,
                },
            )

            # Задержка между отправками
            time.sleep(delay)

        # Завершаем рассылку
        mailing.status = "completed"
        mailing.completed_at = timezone.now()
        mailing.save()
        return {
            "status": "completed",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total": total,
        }

    except Mailing.DoesNotExist:
        return {"status": "error", "message": "Рассылка не найдена"}

    except Exception as e:
        # В случае критической ошибки
        if "mailing" in locals():
            mailing.status = "failed"
            mailing.completed_at = timezone.now()
            mailing.save()

        # Логируем ошибку
        logger.error(f"Ошибка в send_mailing_task: {str(e)}", exc_info=True)

        return {"status": "error", "message": str(e)}
