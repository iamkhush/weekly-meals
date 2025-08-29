"""
ASGI config for weekly_meals project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weekly_meals.settings')

django_app = get_asgi_application()

async def application(scope, receive, send):
    if scope['type'] == 'http':
        scope['root_path'] = os.environ.get('SCRIPT_NAME', '')
    await django_app(scope, receive, send)
