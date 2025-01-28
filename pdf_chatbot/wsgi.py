import os
from django.core.wsgi import get_wsgi_application

print("WSGI application starting...")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_chatbot.settings')

try:
    application = get_wsgi_application()
    print("WSGI application loaded successfully.")
except Exception as e:
    print(f"WSGI error: {e}")

app = application


