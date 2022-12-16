import os

import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "=================================================="

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'djangowebix',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME':  os.environ.get('DATABASE_NAME', 'djangowebix_test'),
        },
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",

  #  "sorl.thumbnail",

    "django_webix",
    'django_webix.contrib.admin',
    'django_webix.contrib.auth',
    'feincms', # to remove in future
    #'hijack', # 2.3.0
    'django_dal',
    "django_filtersmerger",
    "tests.app_name"
]

ROOT_URLCONF = 'tests.urls'

SITE_ID = 1

MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        #'hijack.middleware.HijackUserMiddleware',
        'django_dal.middleware.ContextParamsMiddleware',
    )


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

CONTEXT_PARAMS = 'tests.app_name.context_params.TestContextParams'


FILTER_MERGER_CLASSES = [
#    'django_webix_filter.filters.defaults.DjangoAdvancedOTFWebixFilter',  # advance otf filter
#    'django_webix_filter.filters.defaults.DjangoAdvancedWebixFilter',  # advanced filter
    'django_webix.filters.defaults.DjangoBaseLockedWebixFilter',  # id selezioanti da webgis
    'django_webix.filters.defaults.DjangoBaseWebixFilter',  # liste webix
#    'django_webix_leaflet.filters.defaults.SpatialFilter',  # spatial filter (rectangular/polygonal)
#    'django_webix_leaflet.filters.defaults.LocationInfo',  # featureinfo
]
WEBIX_LICENSE = 'PRO' # FREE
WEBIX_VERSION = '9.4.0'
WEBIX_CONTAINER_ID = 'content_right'
WEBIX_FONTAWESOME_CSS_URL = 'fontawesome/css/all.min.css'
WEBIX_FONTAWESOME_VERSION = '5.12.0'
