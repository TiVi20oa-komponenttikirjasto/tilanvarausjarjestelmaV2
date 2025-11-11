import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','tilanvarausjarjestelma.settings')
django.setup()
from django.contrib.auth.models import User as AuthUser
from user.models import AppUser
print('AuthUser count:', AuthUser.objects.count())
print('AppUser count:', AppUser.objects.count())
for a in AuthUser.objects.all():
    profile = getattr(a, 'app_profile', None)
    print(a.id, a.username, a.email, '-> profile:', profile.idNumber if profile else None)
