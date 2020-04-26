from .base import *

DEBUG = False
ALLOWED_HOSTS = ["musixbot.herokuapp.com"]

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