from django.test import TestCase
from user.models import Event, Space

# Haetaan ensimmäinen tila testidataa varten
space = Space.objects.first()

# Luodaan testitapahtumia: yksi varattu ja yksi vapaa
Event.objects.create(space=space, title="varattu", start="2025-08-21T10:00:00", end="2025-08-21T12:00:00")
Event.objects.create(space=space, title="vapaa", start="2025-08-22T10:00:00", end="2025-08-22T12:00:00")

# Tänne voit lisätä varsinaiset testitapaukset
