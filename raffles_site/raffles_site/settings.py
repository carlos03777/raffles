import os
from pathlib import Path

# === BASE PATH ===============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# === SEGURIDAD ===============================================================

SECRET_KEY = "django-insecure-_d5c+!6=hp)i$nh#ny8+_omvumpe)k20@_ez9vnk4xp0ud1i7v"

DEBUG = True

# Hosts permitidos 
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# === APLICACIONES ============================================================

INSTALLED_APPS = [
    # Terceros
    "jazzmin",
    "django_crontab",

    # Django base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Aplicaciones locales
    "raffles_app",
]

# === MIDDLEWARE ==============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === URLS Y WSGI =============================================================

ROOT_URLCONF = "raffles_site.urls"
WSGI_APPLICATION = "raffles_site.wsgi.application"


# === TEMPLATES ==============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # carpeta global de templates
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

# === BASE DE DATOS ===========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# === VALIDACIÓN DE CONTRASEÑAS ==============================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === INTERNACIONALIZACIÓN Y ZONA HORARIA ====================================

LANGUAGE_CODE = "es-co"           # Idioma por defecto
TIME_ZONE = "America/Bogota"      # Zona horaria local
USE_I18N = True
USE_TZ = True

# === ARCHIVOS ESTÁTICOS Y MEDIOS ============================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino de collectstatic

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === AUTENTICACIÓN Y REDIRECCIONES ==========================================

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# === EMAIL ==================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# ⚠️ En producción, mover estas variables a variables de entorno (.env)
EMAIL_HOST_USER = "carlosforero2025777@gmail.com"
EMAIL_HOST_PASSWORD = "iozo bdoo gugr fff d"  # contraseña de aplicación, nunca la real
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# === CRONJOBS ==============================================================

CRONJOBS = [
    ("*/10 * * * *", "django.core.management.call_command", ["close_raffles"]),
]

# === PAGOS (WOMPI) ==========================================================

# ⚠️ En producción usar llaves seguras y guardarlas en variables de entorno (.env)
WOMPI_PUBLIC_KEY = "pub_test_KGAaw9rhVA3qwVhmZZNzWPVYjgRYOOUx"
WOMPI_PRIVATE_KEY = "prv_test_wFisBFHGu1zksKJfxeL4yozBgENpcS5A"
WOMPI_EVENTS_SECRET = "test_events_3wbcKjBhc3OBqsB19ItbndJGathPDgUY"
WOMPI_INTEGRITY_SECRET = "test_integrity_oZGoUHob1gD0AFhhDDzuu5EOxXObIVuj"
WOMPI_BASE_URL = "https://sandbox.wompi.co/v1"


# === CLAVE POR DEFECTO ======================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
