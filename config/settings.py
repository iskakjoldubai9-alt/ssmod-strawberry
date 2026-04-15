import os
from pathlib import Path

# Долбоордун негизги папкасы
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-a$k7$&_rpi(heh+=a=#!e9@q7*^!j+fj-q&!jiolbzgc-)4k+y'
DEBUG = True
ALLOWED_HOSTS = ['*']

# --- ТИРКЕМЕЛЕР ---
INSTALLED_APPS = [
    'cloudinary_storage',

    # 2. Django'нун стандарттык тиркемелери
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # Бул жерде турганы оң
    'django.contrib.sitemaps',
    'django.contrib.sites',

    # 3. Cloudinary өзү (staticfiles'тан кийин турса болот)
    'cloudinary',

    # 4. Сиздин тиркемелер
    'shop',
]
SITE_ID = 1
# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Статика үчүн
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
        'DIRS': [], # Эгер өзүнчө папка болсо, [os.path.join(BASE_DIR, 'templates')] деп жазыңыз
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media', # Бул видео/сүрөт үчүн маанилүү
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- ТИЛ ЖАНА УБАКЫТ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

# --- СТАТИКАЛЫК ФАЙЛДАР (CSS, JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise сактагычы
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# --- CLOUDINARY ЖӨНДӨӨЛӨРҮ (Медиа үчүн) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dtuyalp6m',
    'API_KEY': '636667862685854',
    'API_SECRET': 'PgRp9Z7dBhdkoVTk0K1sa1I1390'
}

# Файлдарды (сүрөт/видео) Cloudinary'ге сактоо
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise видеолорду таанышы үчүн
WHITENOISE_MIME_TYPES = {
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.webm': 'video/webm',
}

# --- ТЕЛЕГРАМ ---
TELEGRAM_BOT_TOKEN = '8450866956:AAFYekwt1Sgcz606O46tB37mKAmI3Tsptd4'
TELEGRAM_CHAT_ID = '7678418524'
DELIVERY_USER_CHAT_ID = '6365816184'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'