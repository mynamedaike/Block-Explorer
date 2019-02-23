from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from datetime import timedelta
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NUChain.settings')

app = Celery('NUChainExplorer', broker='redis://localhost')

app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': 'redis://localhost:6379/0',
        'default_timeout': 60 * 60
    }
}

CELERY_IMPORTS = (
    'NUChainExplorer.tasks',
)

app.conf.update(
    
    CELERYBEAT_SCHEDULE = {
        'writeDataToDB': {
            'task': 'writeDataToDB',
            'schedule': timedelta(seconds = 3)          
        }
    }
)

app.autodiscover_tasks()