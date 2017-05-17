web: gunicorn manage:app
worker: celery worker -A --app=celery_runner.app