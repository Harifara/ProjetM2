import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .utils import log_audit

# Exemple : finance/middleware.py ou stock/middleware.py
import os

from django.contrib.auth.models import AnonymousUser


class AuthServiceMiddleware:
    """
    Vérifie le token JWT auprès du Auth Service et ajoute un user temporaire à request.user
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_service_url = os.environ.get("AUTH_SERVICE_URL", "http://auth_service:8000").rstrip('/')

    def __call__(self, request):
        token = request.headers.get("Authorization")
        request.user = AnonymousUser()

        if token:
            try:
                response = requests.get(
                    f"{self.auth_service_url}/api/verify-token/",
                    headers={"Authorization": token},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()

                    class TempUser:
                        def __init__(self, id, username, role):
                            self.id = id
                            self.username = username
                            self.role = role
                            self.is_authenticated = True

                        def __str__(self):
                            return self.username

                    request.user = TempUser(
                        id=data.get("id"),
                        username=data.get("username"),
                        role=data.get("role", "employee")
                    )

            except requests.RequestException as e:
                print(f"❌ AuthServiceMiddleware error: {e}")

        return self.get_response(request)


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            log_audit(
                user_id=getattr(request, 'user_id', None),
                action_type=f'{request.method}_{request.path}',
                details={
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code
                },
                request=request
            )

        return response


