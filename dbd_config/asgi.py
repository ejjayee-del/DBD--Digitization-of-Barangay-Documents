"""
ASGI config for dbd_config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from .startup import apply_startup_migrations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbd_config.settings')

apply_startup_migrations()

application = get_asgi_application()
