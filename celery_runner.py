import os
from app import create_app
import datetime
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, backend=os.environ['REDIS_URL'], 
        broker=os.environ['REDIS_URL']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task
    
    class ContextTask(TaskBase):
        abstract = True
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    
    celery.Task = ContextTask
    
    return celery
    
flask_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
celery = make_celery(flask_app)