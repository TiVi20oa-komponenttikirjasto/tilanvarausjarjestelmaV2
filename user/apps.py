# KIRJASTOJEN JA MODUULIEN LATAUKSET
# ==================================

from django.apps import AppConfig

# Käyttäjä-sovelluksen konfiguraatio
class UserConfig(AppConfig):
    """
    Configuration class for the user application.
    Sets the default auto field and app name.

    Args:
        default_auto_field (str): BigAutoField to use by default for model primary keys.
        name (str): The name of the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    def ready(self):
        # Re-enable the post_save signal handler so that newly-created
        # Django auth.Users are accompanied by an app-level User (idNumber)
        # This creates app.User rows for users created via registration or
        # via the admin. The handler is written to be best-effort and
        # non-blocking.
        try:
            from . import signals  # noqa: F401
        except Exception:
            # If signals fail to import, do not block app startup.
            pass

# Tilat-sovelluksen konfiguraatio
class SpaceConfig(AppConfig):
    """
    Configuration class for the space application.
    Sets the default auto field and app name.

    Args:
        default_auto_field (str): BigAutoField to use by default for model primary keys.
        name (str): The name of the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'space'