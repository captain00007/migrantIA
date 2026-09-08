"""
Django settings for migrantIA project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-Party Apps
    'rest_framework',
    'pgvector.django',

    # MigrantIA Domain Apps
    'apps.chat.apps.ChatConfig',
    'apps.knowledge.apps.KnowledgeConfig',
    'apps.sources.apps.SourcesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://migrantia_user:migrantia_password@localhost:5433/migrantia')
DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# MigrantIA - Configurações de Inteligência Artificial (LLM & Embeddings)
# =============================================================================

# Provedor e Modelo Ativos para LLM (Geração de Texto / Chat / Agente)
AI_LLM_PROVIDER = os.environ.get('AI_LLM_PROVIDER')
AI_LLM_MODEL = os.environ.get('AI_LLM_MODEL')

# Provedor e Modelo Ativos para Embeddings (Vetorização e Busca Semântica)
AI_EMBEDDING_PROVIDER = os.environ.get('AI_EMBEDDING_PROVIDER')
AI_EMBEDDING_MODEL = os.environ.get('AI_EMBEDDING_MODEL')

AI_EMBEDDING_DIMENSIONS = os.environ.get('AI_EMBEDDING_DIMENSIONS')

# Configurações Específicas dos Provedores
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_LLM_MODEL = os.environ.get('OPENAI_LLM_MODEL')
OPENAI_EMBEDDING_MODEL = os.environ.get('OPENAI_EMBEDDING_MODEL')

OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL')
OLLAMA_LLM_MODEL = os.environ.get('OLLAMA_LLM_MODEL')
OLLAMA_EMBEDDING_MODEL = os.environ.get('OLLAMA_EMBEDDING_MODEL')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_LLM_MODEL = os.environ.get('GEMINI_LLM_MODEL')
GEMINI_EMBEDDING_MODEL = os.environ.get('GEMINI_EMBEDDING_MODEL')

TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
