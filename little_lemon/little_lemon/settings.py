import os
from pathlib import Path

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
APPEND_SLASH = False
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cacheops",
    "drf_redesign",
    "rest_framework",
    "rest_framework.authtoken",
    "django_prometheus",
    "django_filters", 
    "djoser",
    "django_seed",
    "LittleLemonAPI",


]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    'django_prometheus.middleware.PrometheusAfterMiddleware',

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
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "little_lemon.wsgi.application"

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
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework.authentication.SessionAuthentication", #TODO - DELETE BEFORE SUBMISSION
        # "rest_framework.authentication.BasicAuthentication",  #TODO - DELETE BEFORE SUBMISSION
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
        'OPTIONS': {
            'sslmode': 'verify-full',
            'sslrootcert': '/Users/terry-brooks/GitHub/coursera-meta-api-final/.postgresql/do-cert.crt',
 
    }
        }
}
CACHEOPS_REDIS = f'redis://{os.getenv('CACHE_USER')}:{os.getenv('CACHE_PASSWORD')}@{os.getenv('CACHE_HOST')}:{os.getenv('CACHE_PORT')}/{os.getenv('CACHE_DB')}'
CACHEOPS_CLIENT_CLASS = 'django_prometheus.cache.backends.redis.RedisCache'

CACHES = {
    "default": {
        "BACKEND": CACHEOPS_CLIENT_CLASS,
        "LOCATION": CACHEOPS_REDIS,
    }
}

CACHEOPS_DEFAULTS = {
    'timeout': 60*60
}
CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60*15},
    'auth.*': {'ops': ('fetch', 'get')},
    'auth.permission': {'ops': 'all'},
    'LittleLemonAPI.*': {},
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
