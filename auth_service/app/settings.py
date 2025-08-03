# auth_service/app/settings.py



import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")  # Обязательная переменная
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# Отладочная информация
print(f"🔧 DEBUG: {DEBUG}")
print(f"🔧 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔧 Переменные окружения ALLOWED_HOSTS: {os.getenv('ALLOWED_HOSTS', 'НЕ НАЙДЕНО')}")

# Принудительное отключение валидации хоста для разработки
if DEBUG:
    ALLOWED_HOSTS = ['*']
    # Дополнительные настройки для обхода проблемы
    USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    
    'django_ratelimit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'app.urls'
ASGI_APPLICATION = 'app.asgi.application'

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

DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/team_platform_auth')
    )
}

# Кэш настройки для django-ratelimit
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis_cache:6379/1',  # База 1 для кэша
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',       
        
        'login_ip': '60/hour',    
        'login_email': '50/hour',     
        
        'password_reset_email': '10/hour',  
        'password_reset_ip': '20/hour', 
        
        'register_email': '20/hour',       
        'register_ip': '30/hour',    
        
        'verify_code_email': '20/hour',
        'verify_code_ip': '20/hour',    
        
        'resend_code_email': '30/hour',
        'resend_code_ip': '30/hour',    
        
        'set_password_email': '20/hour',
        'set_password_ip': '30/hour',    
        
        'email_change_email': '10/hour',   
        'email_change_ip': '20/hour',     
    }
}

SIMPLE_JWT = {
    # Удобно для пользователей - долго не выходят  
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),   # 30 дней
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),  # 90 дней
    
    # Автообновление токенов
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Кастомные поля в токене
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Алгоритм
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

AUTH_USER_MODEL = 'accounts.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

# Email (через Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Celery
CELERY_BROKER_URL = 'redis://redis_cache:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
