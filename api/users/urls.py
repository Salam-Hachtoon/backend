from . import views
from django.urls import path


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path("google/login", views., name="google_login"),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
]
