# ishemalink_api/settings.py

from pathlib import Path

# This tells the computer where our folder is
BASE_DIR = Path(__file__).resolve().parent.parent

# Don't share this secret key with anyone!
SECRET_KEY = "django-insecure-kaxz67_ueo0a-nkj%r(y!ko#3(d9(qt38)@&+vqd101^tjjxe*"

# Leave this on so we can see errors while we learn
DEBUG = True

ALLOWED_HOSTS = []

# This is the list of apps we made
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    'rest_framework', # This is for our API stuff
    'core',
    'domestic',
    'international',
]

# Django uses these to process requests
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ishemalink_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ishemalink_api.wsgi.application"

# This is where all our package data lives
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Checking for strong passwords
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Time and Language
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- BEGINNER ADDITIONS AT THE BOTTOM ---

# This tells Django to use the special User we made in core
AUTH_USER_MODEL = 'core.User'

# This is Task 4: The sticky note memory
# I FIXED THE ERROR: changed '.caches.' to '.cache.'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ishemalink-fast-memory',
    }
}
