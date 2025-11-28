# KIRJASTOJEN JA MODUULIEN LATAUKSET
# =========

from django.db import models
# Avoid importing Django's auth User into the name `User` here; alias it
# so this module can safely define its own app-level `User` model class later.
from django.contrib.auth.models import User as AuthUser
from django.conf import settings
from django.http import JsonResponse
from django.utils.text import slugify


# App-level user profile that provides an app-specific numeric id (User-ID)
class AppUser(models.Model):
    """One-to-one profile for Django auth.User that provides an app-level idNumber.

    This keeps a small app-specific table while still using Django's auth.User
    for authentication.
    """
    idNumber = models.BigAutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='app_profile')
    firstname = models.CharField(max_length=255, blank=True, default='')
    lastname = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    joined_date = models.DateField(null=True, blank=True)
    slug = models.SlugField(default='', blank=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}" if (self.firstname or self.lastname) else f"app-user-{self.idNumber}"


# # MALLIT JOTKA MÄÄRITTELEVÄT SOVELLUKSEN TIETOKANTARAKENTEEN
# # ======================================================

# Malli joka kuvaa uutta tilaa sovelluksessa.
class Space(models.Model):
    """Model representing a space in the application.

    Fields added: `address` and `municipality` (both optional) to provide
    street-level address and municipality display on space cards.
    """

    idNumber = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='space',
        null=True,
        blank=True,
        verbose_name='Owner'
    )

    # Free-form location (legacy). Prefer `address` for detailed street info.
    location = models.CharField(max_length=255, null=False)

    # Optional detailed address (street address) shown on space cards
    address = models.CharField(max_length=255, blank=True, default='')

    # Municipality / city for display (paikkakunta)
    municipality = models.CharField(max_length=128, blank=True, default='')

    publicity = models.CharField(
        max_length=20,
        choices=[
            ('', 'Valitse tilan julkisuus'),
            ('private', 'Yksityinen'),
            ('public', 'Julkinen')
        ],
        default=''
    )

    service_type = models.CharField(
        max_length=20,
        choices=[
            ('', 'Valitse tilan palvelutyyppi'),
            ('rental', 'Vuokra'),
            ('loan', 'Laina')
        ],
        default=''
    )

    type = models.CharField(
        max_length=20,
        choices=[
            ('', 'Valitse tilan tyyppi'),
            ('office', 'Toimisto'),
            ('meeting_room', 'Kokoushuone'),
            ('conference_room', 'Konferenssihuone'),
            ('event_space', 'Tapahtumatila')
        ],
        default=''
    )

    size = models.CharField(max_length=10, verbose_name="Size m²", default="0", blank=True)
    capacity = models.CharField(max_length=10, verbose_name="Capacity", default="0", blank=True)
    slug = models.SlugField(default="", null=False)

    def save(self, *args, **kwargs):
        # Ensure the instance is saved so a primary key exists for slug generation.
        created = self.pk is None
        if created:
            super().save(*args, **kwargs)

        # Generate slug if missing (after instance has a primary key)
        if not self.slug:
            base_slug = slugify(f"{self.type}-{self.location}-{self.idNumber}")
            self.slug = base_slug

        # Always save to persist any changes (address, municipality, etc.)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ID: {self.idNumber}"

# Malli joka kuvaa yksittäistä varausta sovelluksessa.
class Event(models.Model):
    """
    Model representing a single reservation (event) in the application.

    Args:
        space (ForeignKey): Reference to the reserved space
        user (ForeignKey): Reference to the user who made the reservation
        title (CharField): Reservation status or description (e.g. "varattu" or "vapaa")
        start (DateTime): Start time of the reservation
        end (DateTime): End time of the reservation

    Returns:
        str: String representation of the event
    """
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
    reserver_email = models.EmailField('sähköposti', max_length=254, null=True, blank=True, help_text="Varaajan sähköpostiosoite (kirjautunut tai manuaalisesti annettu)")
    title = models.CharField(max_length=200)  # "varattu" tai "vapaa"
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)

    class Meta:
        # Mallitasolla oletusjärjestys: aikaisin aloitus ensin, sitten id
        ordering = ['start', 'id']

    def __str__(self):
        return f"{self.title} ({self.reserver_email or 'ei sähköpostia'})"