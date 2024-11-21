import os
from pathlib import Path
from logtail import LogtailHandler
from loguru import logger
import sys
import pathlib
import warnings
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

import logging
from loguru import logger
def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f" {message}")

warnings.filterwarnings(action='ignore', message=r"w+", )

warnings.showwarning = log_warning

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
PROMETHEUS_METRIC_NAMESPACE = "little_lemon_api"
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
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
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
    "drf_spectacular",
    "LittleLemonAPI",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": ['/Users/terry-brooks/GitHub/coursera-meta-api-final/.venv/lib/python3.12/site-packages/drf_redesign/templates'],
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
        "rest_framework.authentication.SessionAuthentication",  # TODO - DELETE BEFORE SUBMISSION
        "rest_framework.authentication.BasicAuthentication",  # TODO - DELETE BEFORE SUBMISSION
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_THROTTLE_RATES": {"anon": "4/minute", "user": "12/minute"},
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
    
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'The Little Lemon API',
    'DESCRIPTION': 'The Little Lemon API project is Terry Brooks\' final project for Meta\'s APIs course on Coursera. For more information about the course, visit the Coursera course page. The source code for this project is available on GitHub for learning purposes.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
        "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True
        },
    'SWAGGER_UI_DIST': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest',
    'SWAGGER_UI_FAVICON_HREF': "https://cdn.littlelemon.xyz/images/logo-little-lemon.pngg",
    'CONTACT': {
        "name": "Terry A. Brooks, Jr.",
        "url": "https://brooksjr.com",
        "email": "terry@brooksjr.com"
    },
    "EXTERNAL_DOCS": {
        "url": "https://www.postman.com/blackberry-py-dev/workspace/little-lemon-meta-apis-final-terry-brooks-jr/collection/20135114-623c0e98-b088-4bff-8ee7-f8d030294a09?action=share&source=copy-link&creator=20135114",
        "description": "Postman Documentation and full API documentation Hub"
    }

    # OTHERTINGS
}
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Little Lemon API Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Little Lemon API",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Little Lemon",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "cdn.little-lemon.xyz/images/logo-little-lemon.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "cdn.little-lemon.xyz/images/logo-little-lemon.png",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": "cdn.little-lemon.xyz/images/logo-little-lemon.png",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Little Little Lemon API",

    # Copyright on the footer
    "copyright": "Blackberry-Py Dev",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    "search_model": ["auth.User", "auth.Group", 'LittleLemonAPI.Cart', 'LittleLemonAPI.Order', 'LittleLemonAPI.OrderItem', 'LittleLemonAPI.MenuItem', 'LittleLemonAPI.Category'],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app":"LittleLemonAPI"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/terry-brooksjr/little-lemon/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth.User", "auth.Group", 'LittleLemonAPI.MenuItem', 'LittleLemonAPI.Cart', 'LittleLemonAPI.Order', 'LittleLemonAPI.OrderItem',  'LittleLemonAPI.Category'],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {

    },

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "LittleLemonAPI.MenuItem":"fa-solid fa-burger",
        "LittleLemonAPI.Cart":"fa-solid fa-cart-shopping",
        "LittleLemonAPI.Order":"fa-solid fa-money-bill-wheat", 
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
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
        'CONN_MAX_AGE': 300,  # Keep connections alive for 5 minutes
        'CONN_HEALTH_CHECKS': True,  # Check
        "OPTIONS": {
            "sslmode": "verify-full",
            "sslrootcert": os.environ["POSTGRES_CERT_FILE"],
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{os.getenv('CACHE_USER')}:{os.getenv('CACHE_PASSWORD')}@{os.getenv('CACHE_HOST')}:{os.getenv('CACHE_PORT')}/{os.getenv('CACHE_DB')}",
        # "KEY_FUNCTION": "little_lemon.utils.cache.KeyFunction",
      "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PICKLE_VERSION": -1,
            "IGNORE_EXCEPTIONS": True,
            "PARSER_CLASS": "redis.connection._HiredisParser",
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",  # Optional, but recommended
            "CONNECTION_POOL_CLASS_KWARGS": {
                "max_connections": 15,  # Customize as needed
                "timeout": 200,  # Customize as needed
            },
            "RETRY_ON_TIMEOUT": True,  # Enable retries on timeouts
            "RETRY": Retry(  # Configure retry strategy
                backoff=ExponentialBackoff(base=0.1, cap=15),
                retries=5
            )
         }   }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
VIEW_CACHE_TTL = int(os.environ['CACHE_TTL'])
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
VIEW_CACHE_TTL = int(os.environ["CACHE_TTL"])


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
BUNNY_USERNAME = os.environ["BUNNY_USERNAME"]
BUNNY_PASSWORD = os.environ["BUNNY_PASSWORD"]
BUNNY_REGION = os.environ["BUNNY_REGION"]
BUNNY_HOSTNAME = os.environ["BUNNY_HOSTNAME"]
BUNNY_BASE_DIR = os.environ["BUNNY_BASE_DIR"]
STATIC_LOCATION = ".staticfiles/"
STATIC_URL = f"https://cdn.little-lemon.xyz/{STATIC_LOCATION}/"
STATIC_ROOT = STATIC_URL
WHITENOISE_MANIFEST_STRICT = False

STORAGES = {
    "staticfiles": {
        "BACKEND": "little_lemon.utils.storage_backends.StaticStorage",
    },
}
STATICFILES_DIRS = [
  "/Users/terry-brooks/GitHub/coursera-meta-api-final/.venv/lib/python3.12/site-packages/drf_redesign/templates"]
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

DEBUG_LOG_FILE = os.path.join(BASE_DIR, "logs", "little_lemon_debug_log.log")
logtail = LogtailHandler(source_token=os.getenv("LOGTAIL_SOURCE_TOKEN"))
logger.remove(0)
warnings.showwarning = logger.warning
logger.add(DEBUG_LOG_FILE, level="DEBUG", colorize=True, diagnose=True)
logger.add(sys.stderr, level="DEBUG", colorize=True, diagnose=True)
logger.add(sys.stdout, level="DEBUG", colorize=True, diagnose=True)
logger.add(logtail, level="INFO", colorize=True)
logging.basicConfig(level=logging.WARNING)
logger.add("file.log", level="DEBUG")