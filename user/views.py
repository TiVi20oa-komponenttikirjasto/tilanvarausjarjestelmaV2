from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.template import loader
from .models import User,Space,Event
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import make_password
from .forms import UserRegistrationForm
import datetime
from django.utils.text import slugify

# Käytetty esimerkissä
# from django.db.models import Q
# https://www.w3schools.com/django/django_queryset_filter.php/ Filtterointi tapoja/suodatustapoja koodiin!

# Pääsivu näkymä applikaatioille
def main(request):
  template = loader.get_template('main.html')
  return HttpResponse(template.render())

# Käyttäjät näkymä applikaatiolle
def user(request):
  mymembers = AuthUser.objects.all().values()
  template = loader.get_template('user/all_members.html')
  context = {
    'mymembers': mymembers,
  }
  
  return HttpResponse(template.render(context, request))

# Käyttäjän yksityiskohtien näkymä applikaatiolle
def users_details(request, slug):
  mymember = User.objects.get(slug=slug)
  template = loader.get_template('user/users_details.html')
  context = {
    'mymember': mymember,
  } 
  return HttpResponse(template.render(context, request))


# Rekisteröinti näkymä applikaatioille
def register(request):
  if request.method == 'POST':
    form = UserRegistrationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.set_password(form.cleaned_data['password'])
      user.save()
      return redirect('registration-success')
  else:
    form = UserRegistrationForm()
  return render(request, 'user/register.html', {'form': form})

# Rekisteröinti onnistui näkymä applikaatioille
def registration_success(request):
  return render(request, 'user/registration_success.html')

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

