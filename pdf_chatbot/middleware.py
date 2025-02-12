import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class CSRFExemptMiddleware(MiddlewareMixin):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        elif any(re.match(url, request.path) for url in settings.CSRF_EXEMPT_URLS):
            setattr(request, '_dont_enforce_csrf_checks', True)

