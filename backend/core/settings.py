import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

SECRET_KEY = 'django-insecure-rag-system-dev-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'apps.chat',
    'apps.knowledge',
    'apps.system',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,
        'OPTIONS': {'context_processors': []},
    },
]

STATIC_URL = 'static/'
STATICFILES_DIRS = []
FRONTEND_DIR = str(PROJECT_ROOT / 'frontend')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# 项目路径配置
DATA_DIR = str(PROJECT_ROOT / 'data')
VECTOR_STORES_DIR = str(PROJECT_ROOT / 'vector_stores')
CHAT_HISTORY_DIR = str(PROJECT_ROOT / 'chat_history')
UPLOADS_DIR = str(PROJECT_ROOT / 'data' / 'uploads')
MD5_INDEX_PATH = str(PROJECT_ROOT / 'vector_stores' / 'md5_index.json')

# DeepSeek API 配置 (可通过环境变量覆盖)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7'))
DEEPSEEK_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '2000'))

# Embedding 配置
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-v4')
# DashScope API Key (用于 embedding)
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', DEEPSEEK_API_KEY)
