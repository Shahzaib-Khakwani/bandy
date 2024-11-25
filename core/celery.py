from celery import Celery
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery("core")
app.config_from_object('django.conf:settings', namespace="CELERY")

app.conf.beat_schedule = {
    'cleanup-unverified-users-every-30-seconds': {
        'task': 'account.tasks.cleanup_unverified_users',  
        'schedule': 36000.0,  
    },
}


app.autodiscover_tasks()