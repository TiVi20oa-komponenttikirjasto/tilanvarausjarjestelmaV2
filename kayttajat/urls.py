from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('kayttajat/', views.kayttajat, name='kayttajat'),
    path('kayttajat/details/<slug:slug>', views.details, name='details'),
    path('testing/', views.testing, name='testing'),
]