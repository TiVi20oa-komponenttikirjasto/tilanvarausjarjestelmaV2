from django.urls import path
from . import views

# Sovelluksen reitit (URLConf)
urlpatterns = [
    # Pääsivu
    path('', views.main, name='main'),

    # Käyttäjien listaus ja yksityiskohdat
    path('user/', views.user, name='user'),
    path('user/users_details/<slug:slug>', views.users_details, name='users_details'),

    # Tilojen listaus ja yksityiskohdat
    path('space/', views.space, name='space'),
    path('space/spaces_details/<slug:slug>', views.spaces_details, name='spaces_details'),

    # Kalenterin tapahtumien haku ja muokkaus
    path('events-json/<int:space_id>/', views.events_json, name='events_json'), # Tapahtumat JSON-muodossa
    path('add-event/', views.add_event, name='add_event'), # Lisää uusi tapahtuma
    path('delete-event/', views.delete_event, name='delete_event'), # Poista tapahtuma
]
