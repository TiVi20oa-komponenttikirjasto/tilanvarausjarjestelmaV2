from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import User,Space, Event
from django.shortcuts import get_object_or_404, render

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

def events_json(request):
    events = Event.objects.all()
    data = []
    for event in events:
        data.append({
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
        })
    return JsonResponse(data, safe=False)