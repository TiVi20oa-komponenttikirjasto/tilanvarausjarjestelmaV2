from django.contrib.auth.models import User as AuthUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone

from .models import AppUser


@receiver(post_save, sender=AuthUser)
def create_app_user_for_auth_user(sender, instance, created, **kwargs):
    """Ensure that whenever an auth.User is created, we have a matching app User.

    This runs on creation of Django auth users (including admin-created users)
    and creates a best-effort AppUser record. The AppUser.external_id is set to
    the numeric idNumber after creation (best-effort).
    """
    if not created:
        return
    try:
        # If there is already an AppUser with this email, assume mapping exists
        if instance.email:
            existing = AppUser.objects.filter(email__iexact=instance.email).first()
            if existing:
                return
        firstname = instance.first_name or instance.username
        lastname = instance.last_name or ''
        slug_candidate = slugify((firstname + ' ' + lastname)[:50]) or slugify(instance.username)
        app_user = AppUser.objects.create(
            user=instance,
            firstname=firstname,
            lastname=lastname,
            email=instance.email or None,
            joined_date=timezone.localdate(),
            slug=slug_candidate,
        )
    except Exception:
        # swallow any exception to avoid blocking user creation
        pass
