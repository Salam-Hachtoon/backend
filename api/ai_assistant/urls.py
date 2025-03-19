from . import views
from django.urls import path, include


urlpatterns = [
    path('upload_attachments/', views.upload_attachments, name='upload_attachments'),
    path('get_summary/', views.get_summary, name='get_summary'),
]