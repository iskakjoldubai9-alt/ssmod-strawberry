import os
import dj_database_url
from pathlib import Path

# Долбоордун негизги папкасы
BASE_DIR = Path(__file__).resolve().parent.parent

# --- КООПСУЗДУК ---
# SECRET_KEY'ди ар дайым Environment Variables аркылуу алуу сунушталат
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-local-only')

# Render'де дайыма False болушу керек. Локалдык режим үчүн Environment Variable колдонсоңуз болот.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*'] # Продакшнда ['ssmod-strawberry-1.onrender.com', 'lux.kg'] кылуу сунушталат

# --- ТИРКЕМЕЛЕР ---
INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'cloudinary',
    'shop',
    'accounts',
]

SITE_ID = 1

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- МААЛЫМАТ БАЗАСЫ (DATABASE) ---
# Локалдык режимде SQLite, серверде PostgreSQL колдонуу үчүн логика:
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- ТИЛ ЖАНА УБАКЫТ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

# --- СТАТИКАЛЫК ФАЙЛДАР ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Whitenoise үчүн статикалык файлдарды кысуу
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CLOUDINARY ЖӨНДӨӨЛӨРҮ ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dtuyalp6m'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '636667862685854'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'PgRp9Z7dBhdkoVTk0K1sa1I1390'),
    'SECURE': True,
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WHITENOISE_MIME_TYPES = {
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.webm': 'video/webm',
}

# --- TELEGRAM BOTS ---
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '8266512637:AAE2LxxouGBmhJLT9BrrAYbx7z4vWxLGZ0g')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', '5106658401')
DELIVERY_BOT_TOKEN = os.environ.get('DELIVERY_BOT_TOKEN', '8450866956:AAFYekwt1Sgcz606O46tB37mKAmI3Tsptd4')
DELIVERY_CHAT_ID = os.environ.get('DELIVERY_CHAT_ID', '6365816184')
SUPPORT_BOT_TOKEN = os.environ.get('SUPPORT_BOT_TOKEN', '8792681892:AAH1uuzIeyVmcyS6VXPCCSlDI4gY9u2fngU')
SUPPORT_CHAT_ID = os.environ.get('SUPPORT_CHAT_ID', '6365816184')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'home'

# --- CSRF КООПСУЗДУГУ ---
CSRF_TRUSTED_ORIGINS = [
    'https://lux.kg',
    'https://www.lux.kg',
    'https://ssmod-strawberry-1.onrender.com'
]