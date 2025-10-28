# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileUpdateForm, UserRegistrationForm
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
    return HttpResponse(template.render({}, request))

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
            # Ensure a corresponding app-level User exists for this auth user.
            try:
                from .models import User as AppUser
            except Exception:
                AppUser = None
            if AppUser:
                try:
                    # If an AppUser with same email exists, don't duplicate.
                    existing = None
                    if user.email:
                        existing = AppUser.objects.filter(email__iexact=user.email).first()
                    if not existing:
                        slug_candidate = slugify((user.first_name + ' ' + user.last_name)[:50]) or slugify(user.username)
                        custom_user = AppUser.objects.create(
                            firstname=user.first_name or user.username,
                            lastname=user.last_name or '',
                            email=user.email or None,
                            joined_date=timezone.localdate(),
                            slug=slug_candidate,
                        )
                        try:
                            custom_user.external_id = str(custom_user.idNumber)
                            custom_user.save(update_fields=['external_id'])
                        except Exception:
                            pass
                except Exception:
                    # best-effort: don't break registration flow on DB errors
                    pass
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
    template = loader.get_template('user/register.html')
    context = {"form": form}
    return HttpResponse(template.render(context, request))

# Kun rekisteröinti onnistuu
def registration_success(request):
    """
    Render a simple registration success page.
    """
    template = loader.get_template('user/registration_success.html')
    return HttpResponse(template.render({}, request))

# Profiili näkymä
@login_required
def profile(request):
    # TODO: Lisää docstringit
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    user = request.user
    return render(request, 'user/profile.html', {'user': user})

# Profiilin muokkaus näkymä
@login_required
def edit_profile(request):
    # TODO: Lisää docstringit
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        if 'edit_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Tiedot tallenettu onnistuneesti.')
            return redirect('edit_profile')
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Salasana vaihdettu onnistuneesti.')
            return redirect('edit_profile')
    else:
        profile_form = ProfileUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)
    return render(request, 'user/edit_profile.html', {'profile_form': profile_form, 'password_form': password_form})

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
    template = loader.get_template('calendar.html')
    return HttpResponse(template.render({}, request))

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

        # If the request is from an authenticated Django user, prefer their account info
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            first_name = first_name or getattr(request.user, 'first_name', '') or getattr(request.user, 'firstname', '')
            last_name = last_name or getattr(request.user, 'last_name', '') or getattr(request.user, 'lastname', '')
            email = email or getattr(request.user, 'email', '')

        # Basic server-side validation
        if not first_name:
            return JsonResponse({"status": "error", "message": "Etunimi vaaditaan."}, status=400)
        if not email:
            return JsonResponse({"status": "error", "message": "Sähköposti vaaditaan."}, status=400)

        # Determine the app-level User object to attach to the Event.
        # If the request comes from an authenticated Django user, prefer that
        # account and create/find the corresponding app User based on the
        # auth user's email or username. Ignore client-supplied reserver info
        # for authenticated users to avoid spoofing.
        user_obj = None
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            # Try match by auth user's email first
            auth_email = (getattr(request.user, 'email', '') or '').strip()
            if auth_email:
                user_obj = User.objects.filter(email__iexact=auth_email).first()
            # Fallback: try matching by slugified username
            if not user_obj:
                slug_candidate = slugify(getattr(request.user, 'username', '') or '')
                if slug_candidate:
                    user_obj = User.objects.filter(slug=slug_candidate).first()
            # If still not found, create a new app User from auth user info
            if not user_obj:
                slug_candidate = slugify(((getattr(request.user, 'first_name', '') or '') + ' ' + (getattr(request.user, 'last_name', '') or ''))[:50]) or slugify(getattr(request.user, 'username', '') or '')
                try:
                    user_obj = User.objects.create(
                        firstname=(getattr(request.user, 'first_name', '') or request.user.username),
                        lastname=(getattr(request.user, 'last_name', '') or ''),
                        email=auth_email or None,
                        joined_date=timezone.localdate(),
                        slug=slug_candidate,
                    )
                    try:
                        user_obj.external_id = str(user_obj.idNumber)
                        user_obj.save(update_fields=['external_id'])
                    except Exception:
                        pass
                except Exception:
                    user_obj = None
        else:
            # Not authenticated: fall back to client-provided reserver info
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