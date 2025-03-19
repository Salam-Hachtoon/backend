import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attachment


@receiver(post_save, sender=Attachment)
def extract_cach_text():
    pass
