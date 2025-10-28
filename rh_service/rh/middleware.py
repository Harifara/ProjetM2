# rh/middleware.py
import os
import requests
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from .utils import log_audit


# ============================================================
# 🔐 AUTH SERVICE MIDDLEWARE (corrigé)
# ============================================================
class AuthServiceMiddleware:
    """
    Vérifie le token JWT auprès du Auth Service (/auth/me)
    et attache un utilisateur temporaire à request.user.
    Compatible avec Docker (http://auth_service:8000).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_service_url = os.environ.get("AUTH_SERVICE_URL", "http://auth_service:8000").rstrip("/")

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        request.user = AnonymousUser()  # par défaut

        # Si pas de token, on laisse passer (DRF gérera les permissions)
        if not auth_header or not auth_header.startswith("Bearer "):
            return self.get_response(request)

        token = auth_header.split(" ")[1]

        try:
            # Vérifie le token et récupère les infos user
            response = requests.get(
                f"{self.auth_service_url}/api/auth/auth/me/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()

                # ✅ Création d’un utilisateur temporaire
                class TempUser:
                    def __init__(self, id, username, email=None, role="employee"):
                        self.id = id
                        self.username = username
                        self.email = email
                        self.role = role
                        self.is_authenticated = True

                    def __str__(self):
                        return f"{self.username} ({self.role})"

                    @property
                    def is_staff(self):
                        return self.role in ["admin", "responsable_rh"]

                    @property
                    def is_superuser(self):
                        return self.role == "admin"

                request.user = TempUser(
                    id=data.get("id"),
                    username=data.get("username"),
                    email=data.get("email"),
                    role=data.get("role", "employee"),
                )

            elif response.status_code == 401:
                return JsonResponse({"detail": "Token invalide ou expiré."}, status=401)

        except requests.RequestException as e:
            print(f"❌ [AuthServiceMiddleware] Erreur de communication avec Auth Service: {e}")
            return JsonResponse(
                {"detail": "Service d’authentification injoignable."},
                status=503
            )

        return self.get_response(request)


# ============================================================
# 🧾 AUDIT LOG MIDDLEWARE
# ============================================================
class AuditLogMiddleware:
    """
    Enregistre les actions API (POST, PUT, PATCH, DELETE) dans les logs d’audit.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            user_id = getattr(request.user, "id", None)
            if user_id and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                action_map = {
                    "POST": "CREATE",
                    "PUT": "UPDATE",
                    "PATCH": "PARTIAL_UPDATE",
                    "DELETE": "DELETE",
                }
                action_type = f"API_{action_map.get(request.method, 'ACTION')}"

                log_audit(
                    user_id=user_id,
                    action_type=action_type,
                    entity_type="API",
                    entity_id=request.path,
                    details={
                        "method": request.method,
                        "path": request.path,
                        "status_code": response.status_code,
                    },
                    request=request,
                )
        except Exception as e:
            print(f"⚠️ [AuditLogMiddleware] Erreur: {e}")

        return response
