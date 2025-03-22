"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import environ, os # type: ignore
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)


ALLOWED_HOSTS = []

# Email configuration using environment variables
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX')
EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT')

# Retrieve the DEEPSEEK_API_KEY from the environment
DEEPSEEK_API_KEY = env('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = env('DEEPSEEK_API_URL')
# Retrieve google credentials
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'oath.apps.OathConfig',
    'ai_assistant.apps.AiAssistantConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
]


# Rest Framework Settings using JWT for authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# JWT Settings for the access and refresh tokens
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),  # Set the access token expiration to 15 minutes
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Set the refresh token expiration to 7 days
    'ROTATE_REFRESH_TOKENS': True,                   # Whether to rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,                # If True, blacklists the old refresh token when a new one is issued
}

# Celery Settings for the background tasks #
# Broker URL for Redis (Celery)
CELERY_BROKER_URL = env('REDAIS_DATABASE_URL')

# Store Celery task results in Redis (Optional)
CELERY_RESULT_BACKEND = env('REDAIS_DATABASE_URL')

# Import task modules for the django project app
CELERY_IMPORTS = ("users.celery_tasks",)

# Set Celery to use the same time zone as Django
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Schedule the Celery task to delete expired tokens every hour
CELERY_BEAT_SCHEDULE = {
    'clean_expired_blacklisted_tokens_every_minute': {
        'task': 'users.celery_tasks.clean_expired_blacklisted_tokens',
        'schedule': crontab(minute='*',),  # Runs at the start of every hour
    },
}


# Djabgo logging settings #
LOGGING ={
    'version': 1,
    'disable_existing_loggers': False, # Keep the default loggers
   'formatters': {
        'verbose': { # Verbose log format output ['INFO 2025-03-13 12:34:56 authentication User login successful']
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': { # Simple log format output ['INFO User login successful']
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
   "handlers": {
        # Define the file handlers for the logs
        "info_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/info.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5MB per log file
            "backupCount": 5,  # Keep 5 old log files
            "formatter": "verbose",
        },
        "request_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/requests.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5MB per log file
            "backupCount": 5,  # Keep 5 old log files
            "formatter": "verbose",
        },
        "emails_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/emails.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5MB per log file
            "backupCount": 5,  # Keep 5 old log files
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/errors.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5MB per log file
            "backupCount": 5,  # Keep 5 old log files
            "formatter": "verbose",
        },
        "attachment_process_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/attachment.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5MB per log file
            "backupCount": 5,  # Keep 5 old log files
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
   'loggers': {
        # Define the loggers for the different parts of the application
       'authentication': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
       'celery_tasks': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
       'user_serializer': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
       'attachment_serializer': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
       'utility_functions': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
       'models': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
       'requests': {
            'handlers': ['request_file'],
            'level': 'ERROR',
            'propagate': False,
        },
       'emails': {
            'handlers': ['emails_file'],
            'level': 'ERROR',
            'propagate': False,
        },
       'attachment': {
            'handlers': ['attachment_process_file'],
            'level': 'ERROR',
            'propagate': False,
        },
   }
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:3000",  # Allow frontend running on a different port
]
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS"
]
CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "x-requested-with",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.example\.com$",
]



ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'users/emails/templates'), # Add the email templates directory
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Media Settings
MEDIA_URL = "/media/"  # Public URL for accessing media files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Directory where uploaded files will be stored

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# The custom user model that will handel the outh
AUTH_USER_MODEL = 'users.User'

