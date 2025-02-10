import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import groq
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here')
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.app', '.vercel.app','*','http://pdfchatbot-production.up.railway.app/']

# Applications definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',  # Custom app
    'widget_tweaks',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',  # Add this
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add this at the top
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL routing
ROOT_URLCONF = 'pdf_chatbot.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'pdf_chatbot.wsgi.application'

# Database settings (SQLite or PostgreSQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',  # Database name
        'USER': 'postgres',  # Username
        'PASSWORD': 'QRSaWneUcHEHPJqhZFNwvikJMEbpzvXa',  # Replace with your actual password
        'HOST': 'autorack.proxy.rlwy.net',  # Remote host
        'PORT': '13367',  # Port number
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICSTORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Groq API settings
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = groq.Client(api_key=GROQ_API_KEY)

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:8000',
    'https://pdf-chatbot.vercel.app/'
]

# CSRF and session settings
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Login redirect URL
LOGIN_REDIRECT_URL = 'chat'
LOGOUT_REDIRECT_URL = 'login'

# Directories for PDFs and FAISS indexes
PDF_DIR = os.path.join(MEDIA_ROOT, 'pdfs')
FAISS_INDEX_DIR = os.path.join(MEDIA_ROOT, 'faiss_indexes')
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'





# ... (existing settings)

# Django Rest Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Token expiration time (optional)
TOKEN_EXPIRED_AFTER_SECONDS = 86400  # 24 hours

# ... (rest of the settings file)

