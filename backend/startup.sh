#!/bin/bash
export DJANGO_SETTINGS_MODULE=curesdev.production
python manage.py migrate && python manage.py collectstatic && gunicorn --workers 2 curesdev.wsgi
