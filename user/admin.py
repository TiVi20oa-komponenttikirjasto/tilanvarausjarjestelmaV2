from django.contrib import admin
from .models import User, Space, Event

# Järjestelmänvalvojan rakenne MemberAdmin luokalle, joka hyödyntää UusiKayttaja-mallia
class MemberAdmin(admin.ModelAdmin):
  """
  Admin interface for managing user instances.

  Args:
      admin (ModelAdmin): The base admin class.
      lsit_display (tuple): Fields to display in the admin list view.
      prepopulated_fields (dict): Fields to auto-populate based on other fields.
  """

  list_display = ("idNumber", "firstname", "lastname", "email", "phone", "joined_date",)
  prepopulated_fields = {"slug": ("firstname", "lastname")}

# Järjestelmänvalvojan rakenne SpaceAdmin luokalle, joka hyödyntää Tilat-mallia
class SpaceAdmin(admin.ModelAdmin):
  """Admin interface for managing space instances.

  Args:
      admin (ModelAdmin): The base admin class.
      list_display (tuple): Fields to display in the admin list view.
      prepopulated_fields (dict): Fields to auto-populate based on other fields.
  """

  list_display = ("idNumber", "location", "publicity", "service_type", "type", "size", "capacity",)
  prepopulated_fields = {"slug": ("type", "location")}

# Varausten hallinta adminissa
class EventAdmin(admin.ModelAdmin):
  """
  Admin interface for managing event instances.

  Args:
    admin (ModelAdmin): The base admin class.
    list_display (tuple): Fields to display in the admin list view.
    list_filter (tuple): Fields to filter in the admin list view.
    search_fields (tuple): Fields to search in the admin list view.
    ordering (tuple): Default ordering for the admin list view.
  """

  list_display = ('title', 'space', 'start_date', 'end_date')
  list_filter = ('space', 'title')
  search_fields = ('title',)
  ordering = ('start', 'id')

  # Metodi joka palauttaa vain alkamis päivämäärän, jotta vältytään aikavyöhykkeisiin liittyviltä ongelmilta
  def start_date(self, obj):
    """_summary_

    Args:
        obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Palauttaa vain päivämäärän osan datetime-arvosta
    return obj.start.date() if obj.start else None
  start_date.admin_order_field = 'start'
  start_date.short_description = 'Start'

  # Metodi joka palauttaa vain loppumis päivämäärän, jotta vältytään aikavyöhykkeisiin liittyviltä ongelmilta
  def end_date(self, obj):
    """_summary_

    Args:
        obj (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Palauttaa vain päivämäärän osan datetime-arvosta
    return obj.end.date() if obj.end else None
  end_date.admin_order_field = 'end'
  end_date.short_description = 'End'


admin.site.register(User, MemberAdmin)
admin.site.register(Space, SpaceAdmin)
admin.site.register(Event, EventAdmin)