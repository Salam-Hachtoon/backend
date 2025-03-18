from . import views
from django.urls import path


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path("google/login", views., name="google_login"),
]
