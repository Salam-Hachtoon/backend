from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration for the 'users' app.
    Attributes:
        default_auto_field (str): Specifies the type of auto-incrementing primary key field to use.
        name (str): The name of the app.
    Methods:
        ready: Imports the signal handlers for the 'users' app.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.userSignal  # Import the signal handlers
