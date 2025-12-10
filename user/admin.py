# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Space, Event

# LUOKAT JA RAKENTEET
# ===================

# Järjestelmänvalvojan rakenne SpaceAdmin luokalle, joka hyödyntää Tilat-mallia
class SpaceAdmin(admin.ModelAdmin):
  """ Interface for managing space instances.

  Args:
      admin (ModelAdmin): The base admin class.
      list_display (tuple): Fields to display in the admin list view.
      prepopulated_fields (dict): Fields to auto-populate based on other fields.
  """

  list_display = ("idNumber", "type", "location", "municipality", "address", "publicity", "service_type", "size", "capacity", "owner")
  exclude = ('idNumber', 'slug')
  search_fields = ("location", "address", "municipality", "owner__username")
  list_filter = ("publicity", "service_type", "type")
  
  # Show address & municipality in the edit form and group commonly edited fields
  fieldsets = (
      (None, { 'fields': ('owner', 'type', 'location', 'address', 'municipality') }),
      ('Details', { 'fields': ('publicity', 'service_type', 'size', 'capacity') }),
  )

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

  list_display = ('title', 'space', 'start_date', 'end_date', 'reserver_email', 'user_id_number')
  list_filter = ('space', 'title')
  search_fields = ('title','user__email','reserver_email','user__id')
  ordering = ('start', 'id')
  readonly_fields = ('user_id_number',)

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
    return obj.user.email if obj.user else obj.reserver_email
  reserver_email.admin_order_field = 'user__email'
  reserver_email.short_description = 'Sähköposti'

  def user_id_number(self, obj):
    """Show the user's numeric ID (default User model)."""
    # Prefer the app-level numeric id (AppUser.idNumber) if a profile exists
    try:
      if obj.user and hasattr(obj.user, 'app_profile') and obj.user.app_profile:
        return obj.user.app_profile.idNumber
      return obj.user.id if obj.user else None
    except Exception:
      return None
  user_id_number.short_description = "User ID"

if admin.site.is_registered(User):
  admin.site.unregister(User)

class AuthUserAdmin(DjangoUserAdmin):
    """Extend Django’s default User admin to show a placeholder app ID field."""
    readonly_fields = DjangoUserAdmin.readonly_fields + ('app_id_number',)
    # Insert the app_id_number column before the staff-status column for clarity
    _base_list = list(DjangoUserAdmin.list_display)
    try:
        _insert_at = _base_list.index('is_staff')
    except ValueError:
        _insert_at = len(_base_list)
    _base_list.insert(_insert_at, 'app_id_number')
    list_display = tuple(_base_list)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'app_id_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def app_id_number(self, obj):
        """Return the app-level User-ID if an AppUser profile exists for this auth.User."""
        try:
            if hasattr(obj, 'app_profile') and obj.app_profile:
                return obj.app_profile.idNumber
        except Exception:
            return None
        return None
    app_id_number.short_description = 'User-ID'

admin.site.register(User, AuthUserAdmin)
admin.site.register(Space, SpaceAdmin)
admin.site.register(Event, EventAdmin)
