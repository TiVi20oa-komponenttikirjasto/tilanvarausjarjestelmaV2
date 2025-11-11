from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Print auth.User -> AppUser profile mappings'

    def handle(self, *args, **options):
        from django.contrib.auth.models import User as AuthUser
        from user.models import AppUser
        self.stdout.write(f'AuthUser count: {AuthUser.objects.count()}')
        self.stdout.write(f'AppUser count: {AppUser.objects.count()}')
        for a in AuthUser.objects.all():
            profile = getattr(a, 'app_profile', None)
            self.stdout.write(f'{a.id}\t{a.username}\t{a.email}\t-> profile: {profile.idNumber if profile else None}')
