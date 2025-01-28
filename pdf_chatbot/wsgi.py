import os
import sys
import traceback
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_chatbot.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print('Error loading the application:')
    print(traceback.format_exc())
    raise e

def handler(event, context):
    try:
        return application(event, context)
    except Exception as e:
        print('Error handling the request:')
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': str(e)
        }




