import os

from .settings import *

DEBUG = True

# SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# ALLOWED_HOSTS = ["localhost", "ymbdp7523p.us-east-1.awsapprunner.com", "*"]
# CSRF_TRUSTED_ORIGINS = ["https://ymbdp7523p.us-east-1.awsapprunner.com/"]

#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
