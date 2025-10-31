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
        # NOTE: We intentionally do NOT auto-import signals here. The project
        # prefers to create app-level User records only explicitly (for example
        # during the registration flow). Avoid registering a global post_save
        # handler that would create app Users for every auth.User (including
        # admin-created users), because that populates the app `User` table
        # when we don't want it.
        # If you need the legacy behavior, re-enable the import below.
        # try:
        #     from . import signals  # noqa: F401
        # except Exception:
        #     pass
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