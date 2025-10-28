import logging
from typing import Optional
from django.http import HttpRequest
from .models import AuditLog

logger = logging.getLogger(__name__)

def get_client_ip(request: HttpRequest) -> Optional[str]:
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", None)
        return ip
    except Exception as e:
        logger.warning(f"Impossible de récupérer l'adresse IP: {e}")
        return None


def log_audit(user, action_type, entity_type=None, entity_id=None, details=None, request=None):
    try:
        audit_data = {
            "user": user if user and getattr(user, "is_authenticated", False) else None,
            "action_type": action_type,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "details": details or {},
        }

        if request:
            audit_data["ip_address"] = get_client_ip(request)
            audit_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")

        return AuditLog.objects.create(**audit_data)
    except Exception as e:
        logger.error(f"Erreur lors de la création du log d’audit: {e}")
        return None
