from django.urls import path
from . import views
from plotlyapp.dash_apps.finished_apps import mainpage #<- Import all plotly apps here.

urlpatterns = [
    path('', views.home, name='home'),
    path('welcome', views.welcome, name='welcome'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('recovery', views.recovery, name='recovery'),
    path('logout', views.logout, name='logout'),
        ]