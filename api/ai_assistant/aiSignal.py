import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attachment
from .celery_tasks import get_text_task

@receiver(post_save, sender=Attachment)
def get_text():
    get_text_task.delay()
