from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    """
    Configuration class for the 'ai_assistant' Django application.
    This class inherits from Django's AppConfig and is used to configure
    application-specific settings for the 'ai_assistant' app.
    Attributes:
        default_auto_field (str): Specifies the type of primary key to use for models
            in this app. Defaults to 'django.db.models.BigAutoField'.
        name (str): The full Python path to the application.
    Methods:
        ready():
            This method is called when the application is ready. It imports the
            `aiSignal` module from the `ai_assistant` package to ensure signal
            handlers are connected.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_assistant'

    def ready(self):
        import ai_assistant.aiSignal
