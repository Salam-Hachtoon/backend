from . import views
from django.urls import path



urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path("auth/google/callback/", views.google_oauth_callback, name="google_oauth_callback"),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('userinfo/', views.userinfo, name='userinfo'),
    path('refresh_token/', views.refresh_token, name='refresh_token'),
    path('update_account/', views.update_account, name='update_account'),
    path('change_password/', views.change_password, name='change_password'),
    path('verfy_otp/', views.verfy_otp, name='verfy_otp'),
]
