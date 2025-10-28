import json
from .utils import log_audit


# Exemple : finance/middleware.py ou stock/middleware.py
import os
import requests
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

        if hasattr(request, 'user') and request.user:
            if isinstance(request.user, dict) and request.user.get('id'):
                if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    action_map = {
                        'POST': 'CREATE',
                        'PUT': 'UPDATE',
                        'PATCH': 'PARTIAL_UPDATE',
                        'DELETE': 'DELETE'
                    }

                    action_type = f"API_{action_map.get(request.method, 'ACTION')}"

                    log_audit(
                        user_id=request.user.get('id'),
                        action_type=action_type,
                        entity_type='API',
                        entity_id=request.path,
                        details={
                            'method': request.method,
                            'path': request.path,
                            'status_code': response.status_code
                        },
                        request=request
                    )

        return response
