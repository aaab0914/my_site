# my_site/settings.py
# ========================================
# Imports
# ========================================

import os
# os: Operating system interface module for reading environment variables

from pathlib import Path
# Path: Object-oriented filesystem paths

from decouple import Csv, config
# config: Function for reading environment variables from .env file
# Csv: Helper for parsing comma-separated values from environment variables

from logging.handlers import RotatingFileHandler
# RotatingFileHandler: Log handler that rotates log files when they reach a certain size

from logging.handlers import TimedRotatingFileHandler
# ========================================
# Build paths inside the project
# ========================================

BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR: Base directory of the project, used for absolute file paths


# ========================================
# Security settings
# ========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-esgyg9h0dut!3$t%g0#b#-@s@b&1&-h$83d0#^1sl1@i6ldx3q")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,testserver", cast=Csv())


# ========================================
# Application definition
# ========================================

SITE_ID = 1

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',

    'blog.apps.BlogConfig',
    'images.apps.ImagesConfig',
    'users.apps.UsersConfig',

    # third-party
    'taggit',
    'markdownx',
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

ROOT_URLCONF = "my_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "my_site.wsgi.application"


# ========================================
# Database configuration
# ========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'blog'),
        'USER': os.environ.get('DB_USER', 'blog'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'StrongPass123!'),
        'HOST': os.environ.get('DB_HOST', 'db' if os.environ.get('RUNNING_IN_DOCKER') else 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# ========================================
# Password validation
# ========================================

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


# ========================================
# Internationalization
# ========================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ========================================
# Static files (CSS, JavaScript, Images)
# ========================================

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Points to the static folder in the project root
]


# ========================================
# Logging configuration
# ========================================

# 确保 logs 目录存在
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGS_DIR / 'access.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ========================================
# Media files (User-uploaded files)
# ========================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'