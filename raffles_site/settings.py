import os
from pathlib import Path
from decouple import config
import dj_database_url

# === BASE PATH ===============================================================

BASE_DIR = Path(__file__).resolve().parent.parent






import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ========== AWS S3 ==========
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-2")

AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"



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
    "storages",
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
# ========== AWS S3 STORAGE CONFIGURATION ==========


# DEBUG EN settings.py
# print("🚀 S3 CONFIGURATION:")
# print(f"DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}")
# print(f"MEDIA_URL: {MEDIA_URL}")
# print(f"AWS_ACCESS_KEY_ID: {'✅ SET' if AWS_ACCESS_KEY_ID else '❌ MISSING'}")


# from django.core.files.storage import default_storage
# print("🧠 STORAGE CLASS EN SETTINGS:", default_storage.__class__)

# from storages.backends.s3boto3 import S3Boto3Storage
# from django.core.files.storage import default_storage
# default_storage.__class__ = S3Boto3Storage


from django.core.files.storage import storages
from storages.backends.s3boto3 import S3Boto3Storage

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
