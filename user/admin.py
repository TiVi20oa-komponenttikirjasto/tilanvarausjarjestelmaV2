# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.contrib import admin
from .models import User, Space, Event
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User as AuthUser

# LUOKAT JA RAKENTEET
# ===================

# Järjestelmänvalvojan rakenne MemberAdmin luokalle, joka hyödyntää UusiKayttaja-mallia
class MemberAdmin(admin.ModelAdmin):
  """ Interface for managing user instances.

  Args:
      admin (ModelAdmin): The base admin class.
      list_display (tuple): Fields to display in the admin list view.
      prepopulated_fields (dict): Fields to auto-populate based on other fields.
  """

  list_display = ("idNumber", "firstname", "lastname", "email", "phone", "joined_date",)
  prepopulated_fields = {"slug": ("firstname", "lastname")}

# Järjestelmänvalvojan rakenne SpaceAdmin luokalle, joka hyödyntää Tilat-mallia
class SpaceAdmin(admin.ModelAdmin):
  """ Interface for managing space instances.

  Args:
      admin (ModelAdmin): The base admin class.
      list_display (tuple): Fields to display in the admin list view.
      prepopulated_fields (dict): Fields to auto-populate based on other fields.
  """

  list_display = ("idNumber", "owner", "location", "publicity", "service_type", "type", "size", "capacity",)
  prepopulated_fields = {"slug": ("type", "location")}

# Varausten hallinta adminissa
class EventAdmin(admin.ModelAdmin):
  """ Interface for managing event instances.

  Args:
    admin (ModelAdmin): The base admin class.
    list_display (tuple): Fields to display in the admin list view.
    list_filter (tuple): Fields to filter in the admin list view.
    search_fields (tuple): Fields to search in the admin list view.
    ordering (tuple): Default ordering for the admin list view.
  """

  list_display = ('title', 'space', 'start_date', 'end_date', 'reserver_email')
  list_filter = ('space', 'title')
  search_fields = ('title','user__email')
  ordering = ('start', 'id')

  # Metodi joka palauttaa vain alkamis päivämäärän, jotta vältytään aikavyöhykkeisiin liittyviltä ongelmilta
  def start_date(self, obj):
    """The start date without time zone issues.

    Args:
        Event (object): The event instance.

    Returns:
         date: The start date of the event, or None if not available
    """
    # Palauttaa vain päivämäärän osan datetime-arvosta
    return obj.start.date() if obj.start else None
  start_date.admin_order_field = 'start'
  start_date.short_description = 'Start'

  # Metodi joka palauttaa vain loppumis päivämäärän, jotta vältytään aikavyöhykkeisiin liittyviltä ongelmilta
  def end_date(self, obj):
    """Returns the end date without timezone issues.

    Args:
        Event (object): The event instance.

    Returns:
        date: The end date of the event, or None if not available
    """
    # Palauttaa vain päivämäärän osan datetime-arvosta
    return obj.end.date() if obj.end else None
  end_date.admin_order_field = 'end'
  end_date.short_description = 'End'

  def reserver_email(self, obj):
    """Return the email address of the user who made the reservation."""
    if obj.user:
      return obj.user.email
    return None
  reserver_email.admin_order_field = 'user__email'
  reserver_email.short_description = 'Sähköposti'

# Rekisteröidään mallit admin-käyttöliittymään
admin.site.register(User, MemberAdmin)
admin.site.register(Space, SpaceAdmin)
admin.site.register(Event, EventAdmin)

# Show the app-specific idNumber on the Django auth.User change form (Personal info)
try:
  admin.site.unregister(AuthUser)
except Exception:
  pass


class AuthUserAdmin(DjangoUserAdmin):
  readonly_fields = DjangoUserAdmin.readonly_fields + ('app_id_number',)

  fieldsets = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'app_id_number')}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login', 'date_joined')}),
  )

  def app_id_number(self, obj):
    try:
      if obj.email:
        app_user = User.objects.filter(email=obj.email).first()
        if app_user:
          return app_user.idNumber
      # fallback: try matching by username/slug
      app_user = User.objects.filter(slug=obj.username).first()
      if app_user:
        return app_user.idNumber
    except Exception:
      return None
    return None

  app_id_number.short_description = 'User-ID'


admin.site.register(AuthUser, AuthUserAdmin)