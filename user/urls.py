# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import register, registration_success

# Sovelluksen reitit (URLConf)
# =============================

urlpatterns = [
    # Pääsivu
    path('', views.main, name='main'),

    # Rekisteröinti
    path('register/', register, name='register'),
    path('registration-success/', registration_success, name='registration-success'),

    # Kirjautuminen ja uloskirjautuminen
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),

    # Profiilin hallinta
    path('profile/', views.profile, name='profile'),
    path('editprofile/', views.edit_profile, name='edit_profile'),

    # Tilan luonti
    path('space/create/', views.create_space, name='create_space'),

    # Käyttäjien listaus ja yksityiskohdat
    path('user/', views.user, name='all_members'),
    path('users_details/<slug:slug>', views.users_details, name='users_details'),

    # Tilojen listaus ja yksityiskohdat
    path('space/', views.space, name='space'),
    path('space/spaces_details/<slug:slug>', views.spaces_details, name='spaces_details'),

    # Kalenterin tapahtumien haku ja muokkaus
    path('events-json/<int:space_id>/', views.events_json, name='events_json'), # Tapahtumat JSON-muodossa
    path('add-event/', views.add_event, name='add_event'), # Lisää uusi tapahtuma
    path('delete-event/', views.delete_event, name='delete_event'), # Poista tapahtuma
]
