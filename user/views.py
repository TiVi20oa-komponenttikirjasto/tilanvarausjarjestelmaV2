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

# Pääsivu näkymä applikaatioille
def main(request):
  template = loader.get_template('main.html')
  return HttpResponse(template.render())

# Käyttäjät näkymä applikaatiolle
def user(request):
  mymembers = User.objects.all().values()
  template = loader.get_template('all_members.html')
  context = {
    'mymembers': mymembers,
  }
  
  return HttpResponse(template.render(context, request))

# Käyttäjän yksityiskohtien näkymä applikaatiolle
def users_details(request, slug):
  mymember = User.objects.get(slug=slug)
  template = loader.get_template('users_details.html')
  context = {
    'mymember': mymember,
  } 
  return HttpResponse(template.render(context, request))

# Tilat näkymä applikaatioille
def space(request):
  myspaces = Space.objects.all().values()
  template = loader.get_template('all_spaces.html')
  context = {
    'myspaces': myspaces,
  }
  
  return HttpResponse(template.render(context, request))

# Tilojen yksityiskohtien näkymä applikaatioille
def spaces_details(request, slug):
    myspaces = get_object_or_404(Space, slug=slug)
    template = loader.get_template('spaces_details.html')
    context = {
        'myspaces': myspaces,
    }
    return HttpResponse(template.render(context, request))

def calendar_view(request):
    return render(request, "calendar.html")

    return JsonResponse(data, safe=False)

def events_json(request, space_id):
    events = Event.objects.filter(space_id=space_id)
    data = []
    for event in events:
        data.append({
            "id": event.id,  # Tämä rivi on tärkeä!
            "title": event.title,
            "start": event.start.date().isoformat(),
            "end": event.end.date().isoformat() if event.end else None,
            "color": "red" if event.title.lower() == "varattu" else "green"
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def add_event(request):
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

@csrf_exempt
def delete_event(request):
  if request.method == "POST":
    data = json.loads(request.body)
    event_id = data.get("id")
    try:
      Event.objects.get(id=event_id).delete()
      return JsonResponse({"status": "ok"})
    except Event.DoesNotExist:
      return JsonResponse({"status": "error", "message": "Varausta ei löytynyt"}, status=404)

