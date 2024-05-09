#!/bin/bash
export DJANGO_SETTINGS_MODULE=palind.production
python manage.py migrate && python manage.py collectstatic && gunicorn --workers 2 palind.wsgi
