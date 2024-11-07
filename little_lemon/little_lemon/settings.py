import os
from pathlib import Path
from logtail import LogtailHandler
from loguru import logger
import sys
import pathlib
import warnings
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True
APPEND_SLASH = True
INTERNAL_IPS = [
    "127.0.0.1",
]
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cachalot",
    "drf_redesign",
    "dynamic_breadcrumbs",
    "rest_framework",
    "rest_framework.authtoken",
    "django_prometheus",
    "django_filters",
    "djoser",
    "django_seed",
    "LittleLemonAPI",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "little_lemon.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "dynamic_breadcrumbs.context_processors.breadcrumbs",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "little_lemon.wsgi.application"

REST_FRAMEWORK = {
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication", #TODO - DELETE BEFORE SUBMISSION
        "rest_framework.authentication.BasicAuthentication",  #TODO - DELETE BEFORE SUBMISSION
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "4/minute", "user": "12/minute"},
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
}
DJOSER = {
    "HIDE_USERS":False,
    "PERMISSIONS":{
    'activation': ['rest_framework.permissions.AllowAny'],
    'password_reset': ['rest_framework.permissions.AllowAny'],
    'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
    'set_password': ['djoser.permissions.CurrentUserOrAdmin'],
    'username_reset': ['rest_framework.permissions.AllowAny'],
    'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
    'set_username': ['djoser.permissions.CurrentUserOrAdmin'],
    'user_create': ['rest_framework.permissions.AllowAny'],
    'user_delete': ['djoser.permissions.CurrentUserOrAdmin'],
    'user': ['rest_framework.permissions.IsAuthenticated'],
    'user_list': ['rest_framework.permissions.IsAuthenticated'],
    'token_create': ['rest_framework.permissions.AllowAny'],
    'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
}
}



# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("PG_DATABASE_HOST"),
        "PORT": os.getenv("PG_DATABASE_PORT"),
        "OPTIONS": {
            "sslmode": "verify-full",
            "sslrootcert": "/Users/terry-brooks/GitHub/coursera-meta-api-final/.postgresql/do-cert.crt",
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{os.getenv('CACHE_USER')}:{os.getenv('CACHE_PASSWORD')}@{os.getenv('CACHE_HOST')}:{os.getenv('CACHE_PORT')}/{os.getenv('CACHE_DB')}",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DEBUG:
    INSTALLED_APPS.insert(6, "debug_toolbar")
    MIDDLEWARE.insert(5, "debug_toolbar.middleware.DebugToolbarMiddleware")

    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.alerts.AlertsPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "cachalot.panels.CachalotPanel",
    ]

DEBUG_LOG_FILE = os.path.join(BASE_DIR, 'logs', 'little_lemon_debug_log.log')
logtail = LogtailHandler(source_token=os.getenv('LOGTAIL_SOURCE_TOKEN'))
logger.remove(0)
warnings.showwarning = logger.warning
logger.add(DEBUG_LOG_FILE, level="DEBUG", colorize=True, diagnose=True)
logger.add(sys.stderr, level="DEBUG", colorize=True, diagnose=True)
logger.add(sys.stdout, level="DEBUG",  colorize=True, diagnose=True)
logger.add(logtail, level="INFO", colorize=True)