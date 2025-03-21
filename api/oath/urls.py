from . import views
from django.urls import path


urlpatterns = [
    path('google/', views.google_login, name='google-login'),
    path('google/callback/', views.google_callback, name='google-callback'),
]
