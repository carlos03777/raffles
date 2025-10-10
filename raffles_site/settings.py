import os
from pathlib import Path
from decouple import config
import dj_database_url

# === BASE PATH ===============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# === SEGURIDAD ===============================================================

SECRET_KEY = config('SECRET_KEY', default='clave-temporal-cambiar')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Seguridad adicional para producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
        
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost,http://127.0.0.1').split(',')

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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 
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
        "DIRS": [BASE_DIR / "templates"],
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

# Configuración AUTOMÁTICA para Railway
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Debug simple
db_engine = DATABASES['default']['ENGINE']
if 'postgresql' in db_engine:
    print(" ¡POSTGRESQL CONECTADO CORRECTAMENTE!")
else:
    print(" Usando SQLite - Verifica DATABASE_URL en Railway")

# === VALIDACIÓN DE CONTRASEÑAS ==============================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === INTERNACIONALIZACIÓN Y ZONA HORARIA ====================================

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# === ARCHIVOS ESTÁTICOS Y MEDIOS ============================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Servir archivos estáticos con Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

# === AUTENTICACIÓN Y REDIRECCIONES ==========================================

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# === EMAIL ==================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='')

# === CRONJOBS ==============================================================

CRONJOBS = [
    ("*/10 * * * *", "django.core.management.call_command", ["close_raffles"]),
]

# === PAGOS (WOMPI) ==========================================================

WOMPI_PUBLIC_KEY = config('WOMPI_PUBLIC_KEY')
WOMPI_PRIVATE_KEY = config('WOMPI_PRIVATE_KEY')
WOMPI_EVENTS_SECRET = config('WOMPI_EVENTS_SECRET')
WOMPI_INTEGRITY_SECRET = config('WOMPI_INTEGRITY_SECRET')
WOMPI_BASE_URL = config('WOMPI_BASE_URL')

# === CLAVE POR DEFECTO ======================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Al final de settings.py - AGREGA ESTO
print("🔍 DATABASE CONFIGURATION CHECK:")
print(f"DATABASE_URL exists: {bool(os.environ.get('DATABASE_URL'))}")
if os.environ.get('DATABASE_URL'):
    db_config = dj_database_url.config(default=os.environ.get('DATABASE_URL'))
    print(f"Database ENGINE: {db_config['ENGINE']}")
    print(f"Database NAME: {db_config['NAME']}")
    print("CONECTADO A POSTGRESQL DE RAILWAY")
else:
    print("PostgreSQL NO DETECTADO - Usando SQLite")

# === SEGURIDAD ===============================================================

# Configuración optimizada para Railway
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Desactiva redirección SSL de Django

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-eb2c9.up.railway.app',
    'https://*.railway.app'
]

ALLOWED_HOSTS = [
    'web-production-eb2c9.up.railway.app',
    '*.railway.app',
    'localhost',
    '127.0.0.1'
]

#========== AWS S3 ====================================
# === CONFIGURACIÓN AWS S3 ===================================================

# === CONFIGURACIÓN AWS S3 ===================================================
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = 'mi-django-app-20251010121711'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

# ✅ CONFIGURACIÓN PROBADA Y FUNCIONANDO
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# ELIMINA completamente la sección STORAGES o déjala así:
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",  # ✅ BACKEND CORRECTO
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# URL importante - SIN /media/ al final
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# ELIMINA el debug de boto3 - puede estar causando el error 500