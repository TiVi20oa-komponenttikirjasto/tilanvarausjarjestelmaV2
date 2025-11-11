# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

# Django
# ------
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import IntegerField
from django.db.models.functions import Cast

# Python
# -----
import datetime
import json

# Omat modulit
# ------------
from .forms import ProfileUpdateForm, UserRegistrationForm, SpaceForm
from .models import Space, Event

# Käytetty esimerkissä
# from django.db.models import Q
# https://www.w3schools.com/django/django_queryset_filter.php/ Filtterointi tapoja/suodatustapoja koodiin!


# FUNKTIOT
# ========

# Pääsivun näkymä
def main(request):
    """Render the application's main page."""
    template = loader.get_template('main.html')
    return HttpResponse(template.render({}, request))


# Rekisteröityminen
def register(request):
    """Handle user registration using Django’s built-in User model."""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Optionally save phone to a Profile model if it exists
            phone = form.cleaned_data.get("phone")
            try:
                from .models import Profile
            except Exception:
                Profile = None
            if Profile and phone:
                Profile.objects.create(user=user, phone=phone)

            # Ensure an AppUser profile exists for this auth.User so the
            # app-specific User-ID is available immediately after
            # registration. Use get_or_create to keep this idempotent.
            try:
                from .models import AppUser
                slug_val = slugify(f"{user.first_name} {user.last_name}") or slugify(user.username)
                AppUser.objects.get_or_create(
                    user=user,
                    defaults={
                        'firstname': user.first_name or '',
                        'lastname': user.last_name or '',
                        'email': user.email or None,
                        'joined_date': timezone.localdate(),
                        'slug': slug_val,
                    }
                )
            except Exception:
                # Do not block registration on profile creation errors
                pass

            return redirect("registration-success")
    else:
        form = UserRegistrationForm()

    template = loader.get_template('user/register.html')
    return HttpResponse(template.render({"form": form}, request))


# Rekisteröinti onnistui
def registration_success(request):
    """Render a simple registration success page."""
    template = loader.get_template('user/registration_success.html')
    return HttpResponse(template.render({}, request))


# Profiilinäkymä
@login_required
def profile(request):
    """Display the currently logged-in user's profile."""
    return render(request, 'user/profile.html', {'user': request.user})


# Profiilin muokkaus
@login_required
def edit_profile(request):
    """Allow a logged-in user to edit profile and password."""
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

    return render(
        request,
        'user/edit_profile.html',
        {'profile_form': profile_form, 'password_form': password_form},
    )


# Tilan luominen (Kirjautuminen vaadittu)
@login_required
def create_space(request):
    """Allow logged-in users to create a Space they own."""
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            space = form.save(commit=False)
            space.owner = request.user
            space.save()
            return redirect('profile')
    else:
        form = SpaceForm()
    return render(request, 'user/create_space.html', {'form': form})


# Käyttäjien listausnäkymä
def users_list(request):
    """List all Django auth users."""
    mymembers = User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name')
    template = loader.get_template('user/all_members.html')
    return HttpResponse(template.render({'mymembers': mymembers}, request))


# Yksittäisen käyttäjän tietojen näkymä
def user_details(request, user_id):
    """Display details for a single Django auth user."""
    mymember = get_object_or_404(User, id=user_id)
    template = loader.get_template('users_details.html')
    return HttpResponse(template.render({'mymember': mymember}, request))


# Tilojen listausnäkymä
def spaces(request):
    """Render a page listing all Space instances."""
    qs = Space.objects.all().annotate(
        size_int=Cast('size', IntegerField()),
        capacity_int=Cast('capacity', IntegerField())
    )

    q_location = request.GET.get('location', '').strip()
    q_type = request.GET.get('type', '').strip()
    q_publicity = request.GET.get('publicity', '').strip()
    q_service = request.GET.get('service_type', '').strip()
    q_min_size = request.GET.get('min_size', '').strip()
    q_max_size = request.GET.get('max_size', '').strip()
    q_min_capacity = request.GET.get('min_capacity', '').strip()
    q_max_capacity = request.GET.get('max_capacity', '').strip()

    if q_location:
        qs = qs.filter(location__icontains=q_location)
    if q_type:
        qs = qs.filter(type=q_type)
    if q_publicity:
        qs = qs.filter(publicity=q_publicity)
    if q_service:
        qs = qs.filter(service_type=q_service)

    try:
        if q_min_size:
            qs = qs.filter(size_int__gte=int(q_min_size))
        if q_max_size:
            qs = qs.filter(size_int__lte=int(q_max_size))
    except ValueError:
        pass

    try:
        if q_min_capacity:
            qs = qs.filter(capacity_int__gte=int(q_min_capacity))
        if q_max_capacity:
            qs = qs.filter(capacity_int__lte=int(q_max_capacity))
    except ValueError:
        pass

    template = loader.get_template('all_spaces.html')
    return HttpResponse(template.render({'myspaces': qs}, request))


# Yksittäisen tilan tietojen näkymä
def spaces_details(request, slug):
    """Render a page showing details for a single space identified by slug."""
    myspaces = get_object_or_404(Space, slug=slug)
    template = loader.get_template('spaces_details.html')
    return HttpResponse(template.render({'myspaces': myspaces}, request))


# Kalenterinäkymä
def calendar_view(request):
    """Render the calendar page."""
    template = loader.get_template('calendar.html')
    return HttpResponse(template.render({}, request))


# Palauttaa tilan tapahtumat JSON-muodossa
def events_json(request, space_id):
    """Return all events for a given space as JSON."""
    events = Event.objects.filter(space_id=space_id).order_by('start')
    data = [
        {
            "id": event.id,
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
            # Prefer the snapshot reserver_email stored on the event (if the
            # reserver filled the booking form). Fall back to the linked
            # app/auth user email when available.
            "user_email": (event.reserver_email or (event.user.email if event.user else None)),
            "color": "red" if event.title.lower() == "varattu" else "green"
        }
        for event in events
    ]
    return JsonResponse(data, safe=False)


# Lisää uusi tapahtuma kalenteriin
@csrf_exempt
def add_event(request):
    """Add a new event to a space's calendar."""
    if request.method == "POST":
        data = json.loads(request.body)
        space_id = data.get("space_id")
        space = get_object_or_404(Space, idNumber=space_id)
        start = timezone.make_aware(datetime.datetime.fromisoformat(data["start"]))
        end = timezone.make_aware(datetime.datetime.fromisoformat(data["end"]))

        today = timezone.localtime(timezone.now()).date()
        if start.date() < today:
            return JsonResponse({"status": "error", "message": "Et voi varata menneitä päiviä."}, status=400)

        overlap = Event.objects.filter(space_id=space_id, start__lt=end, end__gt=start).exists()
        if overlap:
            return JsonResponse({"status": "error", "message": "Päällekkäinen varaus!"}, status=400)

        # Prefer explicit email provided in the booking payload. If none is
        # provided and the request is authenticated, use the auth user's email.
        reserver_email = data.get("email") or (request.user.email if getattr(request, 'user', None) and request.user.is_authenticated else None)

        user_obj = request.user if request.user.is_authenticated else None
        Event.objects.create(
            space=space,
            user=user_obj,
            title=data["title"],
            start=start,
            end=end,
            reserver_email=reserver_email,
        )
        return JsonResponse({"status": "ok"})


# Poistaa tapahtuman kalenterista
@csrf_exempt
def delete_event(request):
    """Delete an event by its ID."""
    if request.method == "POST":
        data = json.loads(request.body)
        event_id = data.get("id")
        try:
            Event.objects.get(id=event_id).delete()
            return JsonResponse({"status": "ok"})
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Varausta ei löytynyt"}, status=404)
