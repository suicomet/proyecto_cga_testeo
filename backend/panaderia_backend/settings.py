from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-dev-only')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Get allowed hosts from environment
allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts if host.strip()]
# Add the specific Railway public domain if the env var is available.
# Django does not support wildcard entries in ALLOWED_HOSTS, so we use the
# exact domain provided by Railway instead of the non-functional '*.railway.app'.
if 'RAILWAY_PUBLIC_DOMAIN' in os.environ:
    railway_public_domain = os.environ['RAILWAY_PUBLIC_DOMAIN'].strip()
    if railway_public_domain and railway_public_domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(railway_public_domain)
# Always allow Railway's internal healthcheck domain so that Railway's
# healthcheck service (which sends Host: healthcheck.railway.app) is never
# rejected by Django's SecurityMiddleware with a 400 DisallowedHost error.
if 'healthcheck.railway.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('healthcheck.railway.app')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    # Local apps
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'panaderia_backend.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'panaderia_backend.wsgi.application'

# Database configuration with Railway compatibility and detailed logging
import logging
logger = logging.getLogger(__name__)

def contains_placeholder(value):
    """Check if a string contains unresolved template placeholders."""
    if not value:
        return False
    # Check for common placeholder patterns: {{...}} and ${{...}}
    return '{{' in str(value) or '${{' in str(value)

def get_db_config():
    """Determine database configuration with detailed logging."""
    # Log available environment variables (mask passwords for security)
    db_vars = ['DATABASE_URL', 'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']
    logger.debug("Checking database environment variables:")
    for var in db_vars:
        value = os.getenv(var)
        if value:
            # Mask password in DATABASE_URL and PGPASSWORD
            if var == 'DATABASE_URL' and '://' in value:
                masked = value.split('://')[0] + '://***:***@' + value.split('@')[-1] if '@' in value else '***'
                logger.debug(f"  {var}: {masked}")
            elif var == 'PGPASSWORD' and value:
                logger.debug(f"  {var}: ***")
            else:
                logger.debug(f"  {var}: {value}")
        else:
            logger.debug(f"  {var}: (not set)")
    
    # Log environment detection
    is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
    is_debug = os.getenv('DEBUG', 'True') == 'True'
    logger.info(f"Environment detection - Railway: {is_railway}, DEBUG: {is_debug}")
    
    # 1. Try DATABASE_URL first (Railway's recommended variable)
    database_url = os.getenv('DATABASE_URL')
    if database_url and not contains_placeholder(database_url):
        logger.info(f"Using DATABASE_URL for database configuration (length: {len(database_url)})")
        return {'default': dj_database_url.config(default=database_url, conn_max_age=600)}
    
    if database_url and contains_placeholder(database_url):
        logger.warning(f"DATABASE_URL contains placeholder: '{database_url[:50]}...' - skipping")
    
    # 2. Try individual PG* variables (Railway also provides these)
    pg_vars = ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']
    pg_values = {var: os.getenv(var) for var in pg_vars}
    
    # Check if all PG* variables exist and don't contain placeholders
    if all(pg_values.values()) and not any(contains_placeholder(val) for val in pg_values.values()):
        logger.info(f"Using PG* environment variables for database configuration")
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': pg_values['PGDATABASE'],
                'USER': pg_values['PGUSER'],
                'PASSWORD': pg_values['PGPASSWORD'],
                'HOST': pg_values['PGHOST'],
                'PORT': pg_values['PGPORT'],
            }
        }
    
    # Check which PG* variables are missing or have placeholders
    missing_or_placeholder = []
    for var, value in pg_values.items():
        if not value:
            missing_or_placeholder.append(f"{var} (not set)")
        elif contains_placeholder(value):
            # Show first 30 chars of placeholder value
            preview = value[:30] + '...' if len(value) > 30 else value
            missing_or_placeholder.append(f"{var} (placeholder: '{preview}')")
    
    if missing_or_placeholder:
        logger.warning(f"PG* variables incomplete or contain placeholders: {', '.join(missing_or_placeholder)}")
    
    # 3. Fallback to appropriate configuration based on environment
    # is_railway and is_debug already defined above
    
    if is_railway:
        # On Railway with no valid PostgreSQL config, use SQLite as ultimate fallback
        # This ensures Django can start and healthcheck works
        sqlite_db_path = os.path.join(BASE_DIR, 'db.sqlite3')
        logger.warning(f"No valid PostgreSQL configuration found on Railway. Using SQLite fallback at: {sqlite_db_path}")
        logger.warning(f"This allows Django to start for healthcheck. Database functionality will be limited.")
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': sqlite_db_path,
            }
        }
    else:
        # Local development fallback
        dev_db_config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'panaderia_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
        
        if is_debug:
            logger.info(f"Using development database configuration: {dev_db_config['HOST']}:{dev_db_config['PORT']}/{dev_db_config['NAME']}")
        else:
            logger.warning(f"No valid database configuration found. Using development defaults (may fail).")
            logger.warning(f"Config: {dev_db_config['HOST']}:{dev_db_config['PORT']}/{dev_db_config['NAME']}")
        
        return {'default': dev_db_config}

# Set DATABASES based on the configuration determined above
DATABASES = get_db_config()

# Log final database configuration (without password)
db_config = DATABASES['default']
masked_config = db_config.copy()
if 'PASSWORD' in masked_config:
    masked_config['PASSWORD'] = '***'
logger.info(f"Final database configuration: {masked_config}")

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS configuration
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    # Remove empty strings from the list
    CORS_ALLOWED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS if origin]

CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Logging — write everything to stderr so it appears in Railway deploy logs.
# DEBUG level is intentionally used here to surface any initialisation issue.
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['stderr'],
        'level': 'DEBUG',
    },
    'loggers': {
        # Django internals — keep at INFO to avoid drowning out app messages.
        'django': {
            'handlers': ['stderr'],
            'level': 'INFO',
            'propagate': False,
        },
        # Show every SQL query so we can spot a hanging DB call.
        'django.db.backends': {
            'handlers': ['stderr'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Our own WSGI bootstrap logger.
        'panaderia_backend.wsgi': {
            'handlers': ['stderr'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# CSRF trusted origins (needed for Django Admin even in DEBUG mode)
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS = [origin for origin in CSRF_TRUSTED_ORIGINS if origin]
if 'RAILWAY_PUBLIC_DOMAIN' in os.environ:
    railway_domain = f"https://{os.environ['RAILWAY_PUBLIC_DOMAIN']}"
    if railway_domain not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_domain)

# Security settings for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGIN_REDIRECT_URL = '/api/catalogo/productos/'
LOGOUT_REDIRECT_URL = '/api-auth/login/'

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# --- NUEVO: Configuración Email para 2FA (Brevo API) ---
# Busca la variable tolerando espacios accidentales en Railway
_brevo_key = os.getenv('BREVO_API_KEY')
if not _brevo_key:
    for k, v in os.environ.items():
        if k.strip() == 'BREVO_API_KEY':
            _brevo_key = v
            break
BREVO_API_KEY = _brevo_key
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'lapaloma.noreply@gmail.com')

# Tiempo de expiración del código 2FA (minutos)
TWO_FACTOR_CODE_EXPIRY_MINUTES = int(os.getenv('TWO_FACTOR_CODE_EXPIRY_MINUTES', '5'))
