"""
Django settings for Food Recipes project.
This file contains all configuration for the Django application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url


# ============================================
# ENVIRONMENT VARIABLES
# ============================================

# Load environment variables from .env file
# This keeps secrets out of version control
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps directory to Python path
# This allows us to import 'accounts' instead of 'apps.accounts'
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))


# ============================================
# SECURITY SETTINGS
# ============================================

# SECURITY WARNING: keep the secret key used in production secret!
# This is used for cryptographic signing - if exposed, attackers can forge sessions
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-fallback-key")

# SECURITY WARNING: don't run with debug turned on in production!
# True shows detailed error pages (development only)
# False shows generic 500 errors (production)
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Which hosts/domains can serve this application
# Prevents HTTP Host header attacks
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ============================================
# APPLICATION DEFINITION
# ============================================

INSTALLED_APPS = [
    # Django built-in apps
    "django.contrib.admin",  # Admin interface
    "django.contrib.auth",  # Authentication system
    "django.contrib.contenttypes",  # Generic relationships
    "django.contrib.sessions",  # Session management
    "django.contrib.messages",  # Flash messages
    "django.contrib.staticfiles",  # Static file management
    "django.contrib.sites",  # Site framework (required by allauth)
    # Third party apps
    "crispy_forms",  # Better form rendering
    "crispy_bootstrap5",  # Bootstrap 5 for crispy
    "allauth",  # Authentication
    "allauth.account",  # Account management
    "allauth.socialaccount",  # Social auth (optional)
    "debug_toolbar",  # Debugging tool
    # Cloudinary (add these two)
    "cloudinary",
    "cloudinary_storage",
    # Local apps (our code)
    "apps.accounts",  # User authentication and profiles
    "apps.recipes",  # Main recipe functionality
    "apps.core",  # Homepage and shared views
    "apps.notifications",  # Activity feed and notifications
]

# ============================================
# DJANGO CRISPY FORMS
# ============================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============================================
# DJANGO ALLAUTH (AUTHENTICATION)
# ============================================

# Site ID is required by django.contrib.sites
SITE_ID = 1

# Authentication backends - how users log in
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # Default Django auth
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth auth
]

# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True  # Email is required
ACCOUNT_USERNAME_REQUIRED = True  # Username is required
ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # Can login with username OR email
ACCOUNT_EMAIL_VERIFICATION = (
    "optional"  # Email verification (set to 'mandatory' for production)
)
LOGIN_REDIRECT_URL = "/"  # Where to go after login
LOGOUT_REDIRECT_URL = "/"  # Where to go after logout

# ============================================
# CUSTOM USER MODEL
# ============================================

# Tell Django to use our custom user model instead of the default
AUTH_USER_MODEL = "accounts.CustomUser"

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # Debug toolbar
    "django.middleware.security.SecurityMiddleware",  # Security enhancements
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # Session management
    "django.middleware.common.CommonMiddleware",  # Common utilities
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # User authentication
    "django.contrib.messages.middleware.MessageMiddleware",  # Flash messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection
    "allauth.account.middleware.AccountMiddleware",  # Allauth middleware
]

# ============================================
# URL CONFIGURATION
# ============================================

ROOT_URLCONF = "config.urls"

# ============================================
# TEMPLATES
# ============================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],  # Look for templates here
        "APP_DIRS": True,  # Also look in app/templates folders
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # Required by allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "notifications.context_processors.unread_notifications",  # Custom
            ],
        },
    },
]

# ============================================
# WSGI APPLICATION
# ============================================

WSGI_APPLICATION = "config.wsgi.application"

# ============================================
# DATABASE
# ============================================

# Parse database URL from environment variable
# Defaults to SQLite for development
# import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,  # Keep connections alive for 600 seconds
    )
}

# ============================================
# PASSWORD VALIDATION
# ============================================

# AUTH_PASSWORD_VALIDATORS = []
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

# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC FILES (CSS, JavaScript, Images)
# ============================================

# URL to use when referring to static files
STATIC_URL = "static/"

# Where to find static files during development
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Where to collect static files for production
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

#  Only include STATICFILES_DIRS if the directory exists
if os.path.exists(os.path.join(BASE_DIR, "static")):
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
else:
    STATICFILES_DIRS = []
# ============================================
# MEDIA FILES (User Uploads)
# ============================================

# URL to serve media files
MEDIA_URL = "/media/"

# Where to store uploaded files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ============================================
# CLOUDINARY SETTINGS
# ============================================

import cloudinary
import cloudinary.uploader
import cloudinary.api

# Get credentials from environment variables
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

# Configure cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE["CLOUD_NAME"],
    api_key=CLOUDINARY_STORAGE["API_KEY"],
    api_secret=CLOUDINARY_STORAGE["API_SECRET"],
)

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
# ============================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ============================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================
# DEBUG TOOLBAR
# ============================================

# Only show debug toolbar to these IPs
INTERNAL_IPS = ["127.0.0.1"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================
# EMAIL SETTINGS
# ============================================

# Get email settings from environment variables
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@foodrecipes.com")


if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT, exist_ok=True)
# ============================================
# PRODUCTION SECURITY SETTINGS
# ============================================
# Tell Django it's behind a proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False  # Don't redirect, Railway already did
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


SESSION_COOKIE_DOMAIN = ".railway.app"
CSRF_COOKIE_DOMAIN = ".railway.app"


# # Security settings - only active when DEBUG=False
# # Security settings - only active when DEBUG=False
# if not DEBUG:
#     # HTTPS settings
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     SECURE_SSL_REDIRECT = True

#     # HSTS (HTTP Strict Transport Security)
#     SECURE_HSTS_SECONDS = 31536000  # 1 year
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True

#     # Other security headers
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     SECURE_BROWSER_XSS_FILTER = True
#     X_FRAME_OPTIONS = "DENY"

#     # Trusted origins for CSRF
#     CSRF_TRUSTED_ORIGINS = [
#         "https://*.railway.app",
#         "https://*.up.railway.app",
#         "https://food-recipes-production.up.railway.app",
#     ]  # domain name
