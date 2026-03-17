import logging
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

class CustomerAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL prefixes that don't require customer authentication
        exempt_prefixes = [
            '/welcome/',
            '/register/',
            '/login/',
            '/logout/',
            '/django-admin/',
            '/i18n/',
            '/static/',
            '/media/',
            '/robots.txt',
            '/sitemap.xml',
        ]

        path = request.path_info
        
        # Check if the current path is exempt (considering potential i18n prefixes)
        # Simplified check to see if any exempt prefix is in the path or path starts with it
        is_exempt = False
        for prefix in exempt_prefixes:
            if path.startswith(prefix) or f'/{request.LANGUAGE_CODE}{prefix}' in path:
                is_exempt = True
                break

        try:
            # Allow access if:
            # 1. User is logged in as an admin/staff (Django Auth)
            # 2. Customer is logged in via session (Our Auth)
            # 3. Path is exempt
            user_authenticated = getattr(request, 'user', None) and request.user.is_authenticated
            customer_logged_in = request.session.get('customer_id')

            if user_authenticated or customer_logged_in or is_exempt:
                return self.get_response(request)

            # Otherwise, redirect to the welcome page
            return redirect('welcome')
        except Exception as e:
            logger.error(f"Middleware Error: {str(e)}")
            # In case of error in middleware, don't crash the whole site if possible
            return self.get_response(request)
