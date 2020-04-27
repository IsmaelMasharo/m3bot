from .common import *

DEBUG = False
ALLOWED_HOSTS = ["https://5f86fd97.ngrok.io", "http://3.84.82.107/"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'm3bot',
        'USER': 'ismael',
        'PASSWORD': 'ismael',
        'HOST': 'localhost',
        'PORT': '',
    }
}