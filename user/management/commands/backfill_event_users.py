from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone

from user.models import Event, User as AppUser

class Command(BaseCommand):
    help = (
        "Backfill Event.user by linking events to app.User rows. "
        "Matches by reserver_email (case-insensitive) or by slugified reserver name. "
        "Supports --apply to persist changes and --create-missing to create app users for unmapped events."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually write changes to the database. Without this flag the command shows a dry-run summary.",
        )
        parser.add_argument(
            "--create-missing",
            action="store_true",
            help=(
                "If an event's reserver cannot be matched to an existing app.User, create a new app.User and link it. "
                "Only used when --apply is also provided."
            ),
        )

    def handle(self, *args, **options):
        apply_changes = options.get("apply", False)
        create_missing = options.get("create_missing", False)

        qs = Event.objects.filter(user__isnull=True)
        total = qs.count()
        self.stdout.write(f"Found {total} Event(s) with no linked app.User")

        mapped = 0
        created_users = 0
        unmapped_events = []

        for ev in qs.select_related():
            app_user = None
            # Try matching by reserver_email first
            email = getattr(ev, "reserver_email", None)
            if email:
                app_user = AppUser.objects.filter(email__iexact=email).first()

            # Next try matching by slug from reserver names
            if not app_user:
                firstname = (getattr(ev, "reserver_firstname", "") or "").strip()
                lastname = (getattr(ev, "reserver_lastname", "") or "").strip()
                if firstname or lastname:
                    slug_val = slugify(f"{firstname} {lastname}")
                    app_user = AppUser.objects.filter(slug=slug_val).first()

            if app_user:
                mapped += 1
                self.stdout.write(f"Mapped Event id={ev.id} -> app.User id={app_user.idNumber} (email={app_user.email})")
                if apply_changes:
                    ev.user = app_user
                    ev.save(update_fields=["user"])
            else:
                unmapped_events.append(ev)
                self.stdout.write(f"Unmapped Event id={ev.id} (reserver_email={email}, name={firstname} {lastname})")

        # Optionally create missing app users and link them
        if apply_changes and create_missing and unmapped_events:
            for ev in unmapped_events:
                firstname = (getattr(ev, "reserver_firstname", "") or "").strip()
                lastname = (getattr(ev, "reserver_lastname", "") or "").strip()
                email = getattr(ev, "reserver_email", None)
                slug_val = slugify(f"{firstname} {lastname}") or f"user-{ev.id}"

                # Don't create if someone else already created one concurrently with same email/slug
                existing = None
                if email:
                    existing = AppUser.objects.filter(email__iexact=email).first()
                if not existing:
                    existing = AppUser.objects.filter(slug=slug_val).first()

                if existing:
                    self.stdout.write(f"Race-mapped Event id={ev.id} -> existing app.User id={existing.idNumber}")
                    ev.user = existing
                    ev.save(update_fields=["user"])
                    mapped += 1
                else:
                    new_user = AppUser.objects.create(
                        firstname=firstname or "",
                        lastname=lastname or "",
                        email=email or None,
                        phone=None,
                        joined_date=timezone.now().date(),
                        slug=slug_val,
                    )
                    created_users += 1
                    ev.user = new_user
                    ev.save(update_fields=["user"])
                    self.stdout.write(f"Created app.User id={new_user.idNumber} and linked Event id={ev.id}")

        # Summary
        self.stdout.write("")
        self.stdout.write(f"Total events processed: {total}")
        self.stdout.write(f"Mapped events: {mapped}")
        self.stdout.write(f"Created app.Users: {created_users}")
        self.stdout.write(f"Unmapped events remaining: {len(unmapped_events) - (created_users if (apply_changes and create_missing) else 0)}")

        if not apply_changes:
            self.stdout.write("")
            self.stdout.write("Dry-run complete. To persist changes, re-run with --apply. To create missing app.Users while applying, add --create-missing.")
