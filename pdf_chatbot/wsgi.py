import os
import logging
from django.core.wsgi import get_wsgi_application

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_chatbot.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    logger.error(f"Error while getting WSGI application: {e}")
    raise

app = application


