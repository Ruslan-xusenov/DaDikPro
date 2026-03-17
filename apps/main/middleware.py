from django.shortcuts import redirect
from django.urls import reverse

class CustomerAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that don't require authentication
        exempt_urls = [
            reverse('welcome'),
            reverse('register_customer'),
            reverse('login'),
            '/django-admin/',
            '/i18n/',
            '/static/',
            '/media/',
            '/robots.txt',
            '/sitemap.xml',
        ]

        # Check if the current path is exempt
        path = request.path_info
        is_exempt = any(path.startswith(url) for url in exempt_urls)

        # Allow access if:
        # 1. User is logged in as an admin/staff
        # 2. Customer is logged in via session
        # 3. Path is exempt
        if request.user.is_authenticated or request.session.get('customer_id') or is_exempt:
            return self.get_response(request)

        # Otherwise, redirect to the welcome page
        return redirect('welcome')
