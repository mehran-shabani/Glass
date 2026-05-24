import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",

    "consultations",
    "webapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = "/static/"

# مسیر خروجی دستور collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"

# مسیر فایل‌های static اختصاصی پروژه
# اگر پوشه static در ریشه پروژه نداری، یا آن را بساز یا این بخش را کامنت کن.
STATICFILES_DIRS = []


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}


# Glass API settings
GLASS_API_KEY = os.getenv("GLASS_API_KEY", "")

GLASS_API_BASE_URL = os.getenv(
    "GLASS_API_BASE_URL",
    "https://glass.health/api/external/v2",
)

GLASS_API_VERSION = os.getenv(
    "GLASS_API_VERSION",
    "glass-5.5",
)

GLASS_API_TIMEOUT_SECONDS = int(
    os.getenv("GLASS_API_TIMEOUT_SECONDS", "120")
)

GLASS_API_AUTH_HEADER = os.getenv(
    "GLASS_API_AUTH_HEADER",
    "Authorization",
)

GLASS_API_AUTH_SCHEME = os.getenv(
    "GLASS_API_AUTH_SCHEME",
    "Bearer",
)

GLASS_API_DEBUG_RAW_RESPONSE = (
    os.getenv("GLASS_API_DEBUG_RAW_RESPONSE", "true").lower() == "true"
)