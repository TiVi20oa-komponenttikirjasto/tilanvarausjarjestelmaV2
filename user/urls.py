from django.urls import path
from . import views
from .views import register, registration_success

urlpatterns = [
    # Main URL
    path('', views.main, name='main'),
    # Käyttäjät URLs
    path('user/', views.user, name='user'),
    path('user/users_details/<slug:slug>', views.users_details, name='users_details'),
    # Rekisteröinti URLs
    path('user/register/', register, name='user-register'),
    path('user/registration-success/', registration_success, name='registration-success'),
    # Tilat URLs
    path('space/', views.space, name='space'),
    path('space/spaces_details/<slug:slug>', views.spaces_details, name='spaces_details'),
    path('events-json/<int:space_id>/', views.events_json, name='events_json'),
    path('add-event/', views.add_event, name='add_event'),
    path('delete-event/', views.delete_event, name='delete_event'),
]