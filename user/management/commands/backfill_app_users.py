from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create AppUser profiles for auth.Users that do not have one yet.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Persist changes. Without --apply only shows dry-run.')

    def handle(self, *args, **options):
        apply_changes = options.get('apply', False)
        from django.contrib.auth.models import User as AuthUser
        from user.models import AppUser

        missing = []
        for a in AuthUser.objects.all():
            if hasattr(a, 'app_profile') and a.app_profile:
                continue
            missing.append(a)

        self.stdout.write(f'Found {len(missing)} auth.User(s) without AppUser profile')
        for a in missing:
            self.stdout.write(f'- {a.id}\t{a.username}\t{a.email}')

        if not apply_changes:
            self.stdout.write('\nDry-run: no changes were made. Rerun with --apply to create profiles.')
            return

        created = 0
        for a in missing:
            try:
                slug_val = slugify((a.first_name or a.username) + ' ' + (a.last_name or ''))[:50]
                app = AppUser.objects.create(
                    user=a,
                    firstname=a.first_name or '',
                    lastname=a.last_name or '',
                    email=a.email or None,
                    joined_date=timezone.localdate(),
                    slug=slug_val,
                )
                created += 1
                self.stdout.write(f'Created AppUser id={app.idNumber} for auth.User id={a.id}')
            except Exception as exc:
                self.stdout.write(f'Failed to create for {a.username}: {exc}')

        self.stdout.write(f'Created {created} AppUser profiles')
