# KIRJASTOJEN JA MODUULIEN LATAUKSET
# =========

from django.db import models
from django.http import JsonResponse

# # MALLIT JOTKA MÄÄRITTELEVÄT SOVELLUKSEN TIETOKANTARAKENTEEN
# ======================================================

# Malli joka kuvaa Uutta käyttäjää sovelluksessa.
class User(models.Model):
  """Model representing a user in the application.

  Args:
      idNumber (BigAutoField): Unique identifier for the user
      firstname (CharField): First name of the user
      lastname (CharField): Last name of the user
      phone (CharField): Phone number of the user (optional)
      email (EmailField): Email address of the user (optional)
      joined_date (DateField): Date when the user joined (optional)
      slug (SlugField): Slug for URL identification

  Returns:
      str: String representation of the user (first and last name).
  """

  idNumber = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
  phone = models.CharField(max_length=11, null=True)
  email = models.EmailField(max_length=255, null=True)
  joined_date = models.DateField(null=True)
  slug = models.SlugField(default="", null=False)

  def __str__(self):
    return f"{self.firstname} {self.lastname}"

# Malli joka kuvaa uutta tilaa sovelluksessa.
class Space(models.Model):
  """Model representing new space in the application.

  Args:
      idNumber (BigAutoField): Unique identifier for the space
      location (CharField): Location of the space
      publicity (CharField): Publicity status of the space (private or public)
      service_type (CharField): Service type of the space (rental or loan)
      type (CharField): Type of the space
      size (CharField): Size of the space in square meters
      capacity (CharField): Capacity of the space
      slug (SlugField): Slug field for URL identification

  Returns:
      str: String representation of the space
  """
  idNumber = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
  location = models.CharField(max_length=255, null=False)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)  # "varattu" tai "vapaa"
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        # Mallitasolla oletusjärjestys: aikaisin aloitus ensin, sitten id
        ordering = ['start', 'id']