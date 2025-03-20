from . import views
from django.urls import path, include


urlpatterns = [
    path('upload_attachments/', views.upload_attachments, name='upload_attachments'),
    path('get_summary/', views.get_summary, name='get_summary'),
    path('get_flash_cards/',  views.get_flash_cards, name='get_flash_cards'),
]
