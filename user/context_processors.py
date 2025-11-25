from django.utils import timezone
from django.db import models
from .models import Event

def reservation_sidebar(request):
    now = timezone.now()

    if not request.user.is_authenticated:
        return {"current_reservations": None}
    
    user_events = Event.objects.filter(
            models.Q(user=request.user) | 
            models.Q(reserver_email=request.user.email)
        ).order_by('-start')
    current_reservations = user_events.filter(end__gte=now)

    for varaus in current_reservations:
        print(varaus.user)
        
    return {
        "current_reservations": current_reservations
    }