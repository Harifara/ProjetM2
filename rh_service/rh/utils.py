import uuid
import requests
from django.conf import settings
from .models import AuditLog


def get_client_ip(request):
    """
    🔍 Récupère l'adresse IP du client depuis la requête HTTP.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_audit(user_id, action_type, entity_type=None, entity_id=None, details=None, request=None):
    """
    🧾 Crée une entrée d’audit compatible UUID.
    - user_id : UUID ou str
    - entity_id : UUID ou str
    - details : dict (stocké en JSON)
    """
    if details is None:
        details = {}

    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    # ✅ Convertir UUIDs en str pour compatibilité JSON
    if user_id is not None and not isinstance(user_id, str):
        user_id = str(user_id)
    if entity_id is not None and not isinstance(entity_id, str):
        entity_id = str(entity_id)

    AuditLog.objects.create(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_user_info(user_id):
    """
    🔗 Récupère les informations d’un utilisateur depuis le service Auth.
    """
    if not user_id:
        return None

    # URL du service d’authentification (modifiable dans settings.py)
    auth_service_url = getattr(settings, "AUTH_SERVICE_URL", "http://auth_service:8000")

    try:
        response = requests.get(f"{auth_service_url}/auth/users/{user_id}/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"error": f"AuthService returned {response.status_code}"}
    except requests.RequestException as e:
        return {"error": str(e)}
