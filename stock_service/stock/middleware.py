import os
import requests
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from .utils import log_audit


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
                    f"{self.auth_service_url}/api/auth/verify-token/",
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


class AuditLogMiddleware(MiddlewareMixin):
    """
    Enregistre un audit log pour chaque modification (POST, PUT, PATCH, DELETE)
    """
    def process_response(self, request, response):
        try:
            if getattr(request.user, "is_authenticated", False) and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                action_map = {
                    'POST': 'CREATE',
                    'PUT': 'UPDATE',
                    'PATCH': 'PARTIAL_UPDATE',
                    'DELETE': 'DELETE'
                }

                # Extraire la ressource depuis l'URL
                parts = [p for p in request.path.split('/') if p]
                resource = parts[-2] if len(parts) >= 2 else (parts[-1] if parts else '')
                action_type = f"{action_map.get(request.method, 'ACTION')}_{resource.upper()}"

                log_audit(
                    user_id=getattr(request.user, 'id', None),
                    action_type=action_type,
                    details={'path': request.path, 'method': request.method},
                    request=request
                )
        except Exception as e:
            print(f"⚠️ AuditLogMiddleware error: {e}")

        return response
