from django.contrib import admin
from .models import User, Space, Event

# Register your models here.

# Järjestelmänvalvojan rakenne MemberAdmin luokalle, joka hyödyntää UusiKayttaja-mallia
class MemberAdmin(admin.ModelAdmin):
  """
  Admin interface for managing user instances.

  Args:
      admin (ModelAdmin): The base admin class.
  """
  list_display = ("idNumber", "firstname", "lastname", "email", "phone", "joined_date",)
  prepopulated_fields = {"slug": ("firstname", "lastname")}

admin.site.register(User, MemberAdmin)


# Järjestelmänvalvojan rakenne SpaceAdmin luokalle, joka hyödyntää Tilat-mallia
class SpaceAdmin(admin.ModelAdmin):
  """Admin interface for managing space instances.

  Args:
      admin (ModelAdmin): The base admin class.
  """
  list_display = ("idNumber", "location", "publicity", "service_type", "type", "size", "capacity",)
  prepopulated_fields = {"slug": ("type", "location")}

admin.site.register(Space, SpaceAdmin)
 
# Varausten hallinta adminissa
class EventAdmin(admin.ModelAdmin):
  """
  Admin interface for managing event instances.

  Args:
    admin (ModelAdmin): The base admin class.
  """
  # Show date-only values in the list to avoid timezone/format confusion
  list_display = ('title', 'space', 'start_date', 'end_date')
  list_filter = ('space', 'title')
  search_fields = ('title',)
  # Default ordering in admin list: earliest start first, tie-breaker by id
  ordering = ('start', 'id')

  def start_date(self, obj):
    # return a date-only representation to avoid timezone shifts in the admin list
    return obj.start.date() if obj.start else None
  start_date.admin_order_field = 'start'
  start_date.short_description = 'Start'

  def end_date(self, obj):
    return obj.end.date() if obj.end else None
  end_date.admin_order_field = 'end'
  end_date.short_description = 'End'

admin.site.register(Event, EventAdmin)