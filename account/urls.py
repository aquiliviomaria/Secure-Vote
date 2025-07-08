from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.account_login, name="account_login"),
    path('register/', views.account_register, name="account_register"),
    path('logout/', views.account_logout, name="account_logout"),
    path('profile/update/', views.profile_update, name='profile_update'),
]
