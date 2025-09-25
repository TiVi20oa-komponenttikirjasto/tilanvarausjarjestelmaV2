from django.db import models
from django.http import JsonResponse

# Create your models here.

# Malli joka kuvaa Uutta käyttäjää sovelluksessa.
class User(models.Model):
  """Model representing a user in the application.

  Args:
      idNumber (int): Unique identifier for the user
      firstname (str): First name of the user
      lastname (str): Last name of the user
      phone (int): Phone number of the user
      email (str): Email address of the user
      joined_date (date): Date when the user joined
      slug (str): Slug field for URL identification

  Returns:
      str: String representation of the user
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
      idNumber (int): Unique identifier for the space
      location (str): Location of the space
      publicity (str): Publicity status of the space (private or public)
      service_type (str): Service type of the space (rental or loan)
      type (str): Type of the space
      size (str): Size of the space in square meters
      capacity (str): Capacity of the space
      slug (str): Slug field for URL identification

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
        title (str): Reservation status or description (e.g. "varattu" or "vapaa")
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