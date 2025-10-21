# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.template import loader
from .models import User,Space,Event
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .forms import UserRegistrationForm
import datetime
from django.utils.text import slugify

# Käytetty esimerkissä
# from django.db.models import Q
# https://www.w3schools.com/django/django_queryset_filter.php/ Filtterointi tapoja/suodatustapoja koodiin!

# FUNKTIOT
# ========

# Pääsivun näkymä
def main(request):
    """Render the application's main page.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Variables:
        template (django.template.Template): Template instance loaded with
            'main.html' via django.template.loader.get_template.

    Returns:
        HttpResponse: Response containing the rendered template.
    """
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

def register(request):
    """
    Display and process the user registration form.

    - Uses UserRegistrationForm to create a django.contrib.auth User.
    - Sets the hashed password.
    - If a Profile model exists in this app, saves the phone field there.
    - Redirects to 'registration-success' on success.
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            # Save phone to Profile if model exists
            phone = form.cleaned_data.get("phone")
            try:
                from .models import Profile
            except Exception:
                Profile = None
            if Profile and phone:
                Profile.objects.create(user=user, phone=phone)
            return redirect("registration-success")
    else:
        form = UserRegistrationForm()
    return render(request, "user/register.html", {"form": form})

# Kun rekisteröinti onnistuu
def registration_success(request):
    """
    Render a simple registration success page.
    """
    return render(request, "user/registration_success.html")

# Käyttäjien listausnäkymä
def user(request):
    """Render a page listing all custom User instances.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Variables:
        mymembers (QuerySet of dict): All users returned as dictionaries via .values().
        template (django.template.Template): Loaded 'all_members.html' template.
        context (dict): Context passed to the template.

    Returns:
        HttpResponse: Rendered page containing the members list.
    """
    mymembers = AuthUser.objects.all().values('id','username','email','first_name','last_name')
    template = loader.get_template('user/all_members.html')
    context = {
        'mymembers': mymembers,
        #'current_user': request.user,
    }
    return HttpResponse(template.render({'mymembers': mymembers}, request))

# Yksittäisen käyttäjien tietojen näkymä
def users_details(request, slug):
    """Render a page showing details for a single user identified by slug.

    Args:
        request (HttpRequest): Incoming HTTP request.
        slug (str): Slug identifying the user.

    Variables:
        mymember (User): The requested User instance.
        template (django.template.Template): Loaded 'users_details.html' template.
        context (dict): Context passed to the template.

    Returns:
        HttpResponse: Rendered user detail page.

    Raises:
        User.DoesNotExist: If no User with the given slug exists (propagates from .get()).
    """
    mymember = User.objects.get(slug=slug)
    template = loader.get_template('users_details.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))

# Tilojen listausnäkymä
def space(request):
    """Render a page listing all Space instances.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Variables:
        myspaces (QuerySet of dict): All spaces returned as dictionaries via .values().
        template (django.template.Template): Loaded 'all_spaces.html' template.
        context (dict): Context passed to the template.

    Returns:
        HttpResponse: Rendered page containing the spaces list.
    """
    myspaces = Space.objects.all().values()
    template = loader.get_template('all_spaces.html')
    context = {
        'myspaces': myspaces,
    }
    return HttpResponse(template.render(context, request))

# Yksittäisen tilan tietojen näkymä
def spaces_details(request, slug):
  """Render a page showing details for a single space identified by slug.

    Args:
        request (HttpRequest): Incoming HTTP request.
        slug (str): Slug identifying the space.

    Variables:
        myspaces (Space): The requested Space instance (object or 404 raised).
        template (django.template.Template): Loaded 'spaces_details.html' template.
        context (dict): Context passed to the template.

    Returns:
        HttpResponse: Rendered space detail page.

    Raises:
        Http404: If no Space with the given slug exists (raised by get_object_or_404).
    """
  myspaces = get_object_or_404(Space, slug=slug)
  template = loader.get_template('spaces_details.html')
  context = {
    'myspaces': myspaces,
  }
  return HttpResponse(template.render(context, request))

# Kalenterinäkymä
def calendar_view(request):
   """Render the calendar page.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Returns:
        HttpResponse: Rendered calendar template via django.shortcuts.render.
    """
   return render(request, "calendar.html")

# Palauttaa tilan tapahtumat JSON-muodossa kalenterille
def events_json(request, space_id):
    """Return all events for a given space as JSON suitable for FullCalendar.

    Args:
        request (HttpRequest): Incoming HTTP request.
        space_id (int or str): Identifier of the Space to fetch events for.

    Variables:
        events (QuerySet): Events filtered by space_id and ordered by 'start'.
        data (list): List of dicts prepared for JSON serialization.

    Returns:
        JsonResponse: JSON array of event objects. Each object contains 'id', 'title',
                      'start' (ISO format), 'end' (ISO format or None), and 'color'.
    """
    events = Event.objects.filter(space_id=space_id).order_by('start')
    data = []
    for event in events:
        data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
            "color": "red" if event.title.lower() == "varattu" else "green"
        })
    return JsonResponse(data, safe=False)

# Lisää uusi tapahtuma kalenteriin
@csrf_exempt
def add_event(request):
    """Add a new event to a space's calendar, checking for overlaps.

    Args:
        request (HttpRequest): Incoming HTTP POST request with JSON body containing:
            - space_id: idNumber of the Space
            - title: Event title
            - start: ISO datetime string
            - end: ISO datetime string

    Variables:
        data (dict): Parsed JSON payload.
        space_id (int): Extracted space identifier.
        start (datetime): Aware start datetime.
        end (datetime): Aware end datetime.
        overlap (bool): Whether a conflicting event exists.

    Returns:
        JsonResponse: {"status": "ok"} on success, or {"status": "error", "message": "..."} with
                      appropriate HTTP status on failure (400 for overlap, 500 for parse errors).
    """
    if request.method == "POST":
        data = json.loads(request.body)
        space_id = data.get("space_id")
        space = Space.objects.get(idNumber=space_id)
        start = timezone.make_aware(datetime.datetime.fromisoformat(data["start"]))
        end = timezone.make_aware(datetime.datetime.fromisoformat(data["end"]))
        # Reject events that start in the past (compare dates in server timezone)
        today = timezone.localtime(timezone.now()).date()
        if start.date() < today:
            return JsonResponse({"status": "error", "message": "Et voi varata menneitä päiviä."}, status=400)
        overlap = Event.objects.filter(
            space_id=space_id,
            start__lt=end,
            end__gt=start
        ).exists()
        if overlap:
            return JsonResponse({"status": "error", "message": "Päällekkäinen varaus!"}, status=400)

        # Collect reserver info (require first_name and email)
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()

        # Basic server-side validation
        if not first_name:
            return JsonResponse({"status": "error", "message": "Etunimi vaaditaan."}, status=400)
        if not email:
            return JsonResponse({"status": "error", "message": "Sähköposti vaaditaan."}, status=400)

        # Find or create a user in the custom User model by email when provided,
        # otherwise create a user entry using a slugified name.
        user_obj = None
        if email:
            user_obj, created = User.objects.get_or_create(email=email, defaults={
                'firstname': first_name or 'Tuntematon',
                'lastname': last_name or '',
                'slug': slugify((first_name + ' ' + last_name)[:50]) if (first_name or last_name) else slugify(email)
            })
        else:
            # If no email, create by name (may duplicate)
            slug_candidate = slugify((first_name + ' ' + last_name)[:50]) or f'user-{timezone.now().timestamp()}'
            user_obj, created = User.objects.get_or_create(slug=slug_candidate, defaults={
                'firstname': first_name or 'Tuntematon',
                'lastname': last_name or '',
                'email': email or None
            })

        event = Event.objects.create(
            space=space,
            user=user_obj,
            title=data["title"],
            start=start,
            end=end
        )
        return JsonResponse({"status": "ok", "event_id": event.id})

# Poistaa tapahtuman kalenterista
@csrf_exempt
def delete_event(request):
    """Delete an event by its ID.

    Args:
        request (HttpRequest): Incoming HTTP POST request with JSON body containing 'id'.

    Variables:
        data (dict): Parsed JSON payload.
        event_id (int): ID of the event to delete.

    Returns:
        JsonResponse: {"status": "ok"} on successful deletion, or
                      {"status": "error", "message": "..."} with 404 if not found.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        event_id = data.get("id")
        try:
            Event.objects.get(id=event_id).delete()
            return JsonResponse({"status": "ok"})
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Varausta ei löytynyt"}, status=404)