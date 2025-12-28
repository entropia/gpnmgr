"""
Django settings for gpnmgr project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-taz^x!e%_-p^!37-@a_8&&%ihj66+v!fi2!h(m1jof)-t5i*qi"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "auditlog",
    "bootstrap",
    "django_bootstrap5",
    "gpnmgr.accounts",
    "gpnmgr.teams",
    "gpnmgr.log"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "gpnmgr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(os.path.dirname(__file__), 'templates'),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": [
                "django.templatetags.static",
                "django.templatetags.i18n",
                "django_bootstrap5.templatetags.django_bootstrap5",
                "gpnmgr.utils.templatetags.fa_checkbox",
                "gpnmgr.utils.templatetags.changelog",
            ],
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.debug",
                "django.contrib.messages.context_processors.messages",
                "gpnmgr.utils.context_processors.settings_context"
            ],
            "debug": DEBUG,
        },
    },
]

WSGI_APPLICATION = "gpnmgr.wsgi.application"

from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = 'accounts.User'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'bootstrap', 'static'),
    os.path.join(BASE_DIR, 'gpnmgr', 'static'),
    #('docs', os.path.join(BASE_DIR, 'gpnmgr', 'static', 'docs')),  # Prefix with /docs
]
STATIC_ROOT = "staticfiles/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

OAUTH_NAME = 'gpnmgr'
OAUTH_SECRET = 'XXXXXXXXXXXXXXXXXXXXX'
OPENID_CONF_URL = 'https://keycloak.example.com/realms/keycloak/.well-known/openid-configuration'
OAUTH_CLIENT_SCOPES = ['openid', 'profile']
OAUTH_DISPLAY_NAME_CLAIM = 'name'
OAUTH_USERNAME_CLAIM = 'preferred_username'
OAUTH_GROUP_CLAIM = 'groups'
OAUTH_EMAIL_CLAIM = 'email'

OAUTH_TEAM_MANAGER_GROUP = 'team-manager'
OAUTH_FEDI_MANAGER_GROUP = 'gts-admin'
OAUTH_ADMIN_GROUP = 'full-access'

LOGIN_URL = reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('user_profile')
OAUTH_GROUP_IGNORE_REGEX = r'ignore group regex'

LDAP_BIND_DN = ''
LDAP_BIND_PASSWORD = ''
LDAP_BIND_URL = ''
LDAP_BASE_DN = 'dc=example,dc=com'
LDAP_USER_PK = 'uid'
LDAP_USER_OU = 'ou=users'
LDAP_GROUP_PK = 'cn'
LDAP_GROUP_OU = 'ou=groups'
LDAP_GROUP_MEMBER_KEY = 'member'
LDAP_GROUP_MANAGER_KEY = 'owner'
LDAP_USER_OBJECT_CLASS = 'inetOrgPerson'
LDAP_GROUP_OBJECT_CLASS = 'groupOfNames'

try:
    from bootstrap.settings import BOOTSTRAP5

    # try to load local settings (for production settings or rpc passwords)
    from .local_settings import *
except ImportError:
    pass

from ldap3 import Server, Connection, ALL, SAFE_RESTARTABLE, AUTO_BIND_NONE

server = Server(LDAP_BIND_URL, get_info=ALL)
LDAP_CONNECTION = Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, auto_bind=AUTO_BIND_NONE)

from .permissions import permissions
PERMISSIONS = permissions
COMMON_PERMISSIONS: list[str] = []
