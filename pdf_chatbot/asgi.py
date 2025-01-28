"""
ASGI config for pdf_chatbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
import logging
from django.core.asgi import get_asgi_application

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_chatbot.settings')

try:
    application = get_asgi_application()
except Exception as e:
    logger.error(f"Error while getting ASGI application: {e}")
    raise
