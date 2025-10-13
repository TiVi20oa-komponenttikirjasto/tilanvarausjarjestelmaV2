from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.template import loader
from .models import User,Space, Event
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
import datetime

# Käytetty esimerkissä
# from django.db.models import Q
# https://www.w3schools.com/django/django_queryset_filter.php/ Filtterointi tapoja/suodatustapoja koodiin!


# Pääsivun näkymä
def main(request):
    """
    Renders the main page of the application.
    """
    template = loader.get_template('main.html')
    return HttpResponse(template.render())


# Käyttäjien listausnäkymä
def user(request):
    """
    Renders a page listing all users in the application.
    """
    mymembers = User.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
        'mymembers': mymembers,
    }
    return HttpResponse(template.render(context, request))


# Yksittäisen käyttäjien tietojen näkymä
def users_details(request, slug):
    """
    Renders a page showing details for a single user.
    """
    mymember = User.objects.get(slug=slug)
    template = loader.get_template('users_details.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


# Tilojen listausnäkymä
def space(request):
    """
    Renders a page listing all spaces in the application.
    """
    myspaces = Space.objects.all().values()
    template = loader.get_template('all_spaces.html')
    context = {
        'myspaces': myspaces,
    }
    return HttpResponse(template.render(context, request))


# Yksittäisen tilan tietojen näkymä
def spaces_details(request, slug):
  """
  Renders a page showing details for a single space.
  """
  myspaces = get_object_or_404(Space, slug=slug)
  template = loader.get_template('spaces_details.html')
  context = {
    'myspaces': myspaces,
  }
  return HttpResponse(template.render(context, request))


# Kalenterinäkymä
def calendar_view(request):
  """
  Renders the calendar page.
  """
  return render(request, "calendar.html")


# Palauttaa tilan tapahtumat JSON-muodossa kalenterille
def events_json(request, space_id):
    """
    Returns all events for a given space as JSON for FullCalendar.
    Events are ordered by start datetime ascending to ensure consistent chronology.
    """
    events = Event.objects.filter(space_id=space_id).order_by('start')
    data = []
    for event in events:
        data.append({
            "id": event.id,  # This line is important!
            "title": event.title,
            # Return full ISO datetimes (naive or timezone-aware depending on your settings).
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
            "color": "red" if event.title.lower() == "varattu" else "green"
        })
    return JsonResponse(data, safe=False)


# Lisää uusi tapahtuma kalenteriin
@csrf_exempt
def add_event(request):
    """
    Adds a new event to the calendar for a given space.
    Checks for overlapping events before creation.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        space_id = data.get("space_id")
        space = Space.objects.get(idNumber=space_id)
        start = timezone.make_aware(datetime.datetime.fromisoformat(data["start"]))
        end = timezone.make_aware(datetime.datetime.fromisoformat(data["end"]))
        # Tarkista päällekkäisyys
        overlap = Event.objects.filter(
            space_id=space_id,
            start__lt=end,
            end__gt=start
        ).exists()
        if overlap:
            return JsonResponse({"status": "error", "message": "Päällekkäinen varaus!"}, status=400)
        space = Space.objects.get(idNumber=space_id)
        Event.objects.create(
            space=space,
            title=data["title"],
            start=start,
            end=end
        )
        return JsonResponse({"status": "ok"})


# Poistaa tapahtuman kalenterista
@csrf_exempt
def delete_event(request):
    """
    Deletes an event from the calendar by its ID.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        event_id = data.get("id")
        try:
            Event.objects.get(id=event_id).delete()
            return JsonResponse({"status": "ok"})
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Varausta ei löytynyt"}, status=404)

