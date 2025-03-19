from . import views
from django.urls import path



urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path("auth/google/callback/", views.google_oauth_callback, name="google_oauth_callback"),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
]
