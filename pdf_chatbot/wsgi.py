"""
WSGI config for pdf_chatbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

# Add the project directory to the Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_chatbot.settings')

from django.core.wsgi import get_wsgi_application

# Get the WSGI application
application = get_wsgi_application()

# Vercel needs the variable to be named 'app'
app = application


