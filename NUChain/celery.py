from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from datetime import timedelta
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NUChain.settings')

app = Celery('NUChainExplorer')

CELERY_IMPORTS = (
    'NUChainExplorer.tasks',
)

app.conf.update(
    BROKER_URL = 'redis://127.0.0.1:6379/2',
    
    CELERYBEAT_SCHEDULE = {
        'writeDataToDB': {
            'task': 'writeDataToDB',
            'schedule': timedelta(seconds = 3)          
        }
    }
)

#app.autodiscover_tasks(settings.INSTALLED_APPS)
app.autodiscover_tasks()