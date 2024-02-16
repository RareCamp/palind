import os

from .settings import *

DEBUG = True

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = [".awsapprunner.com", ".curesdev.com"]
CSRF_TRUSTED_ORIGINS = ["https://*.awsapprunner.com", "https://*.curesdev.com"]

# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
