import os
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_chatbot.settings')

# Collect static files
execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])

application = get_wsgi_application()
app = application


