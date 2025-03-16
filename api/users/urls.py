from . import views
from django.urls import path


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('userinfo/', views.userinfo, name='userinfo'),
    path('refresh_token/', views.refresh_token, name='refresh_token'),
    path('update_account/', views.update_account, name='update_account'),
]
