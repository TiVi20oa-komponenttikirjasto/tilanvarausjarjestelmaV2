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