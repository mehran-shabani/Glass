import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.getenv('SECRET_KEY','dev-secret-key')
DEBUG=True
ALLOWED_HOSTS=['*']
INSTALLED_APPS=[
 'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
 'rest_framework','consultations','webapp']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
LANGUAGE_CODE='en-us';TIME_ZONE='UTC';USE_I18N=True;USE_TZ=True
STATIC_URL='static/'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
GLASS_API_KEY=os.getenv('GLASS_API_KEY','')
GLASS_API_BASE_URL=os.getenv('GLASS_API_BASE_URL','https://glass.health/api/external/v2')
GLASS_API_VERSION=os.getenv('GLASS_API_VERSION','glass-5.5')
GLASS_API_TIMEOUT_SECONDS=int(os.getenv('GLASS_API_TIMEOUT_SECONDS','120'))
