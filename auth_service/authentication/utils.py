import logging
from typing import Optional
from django.http import HttpRequest
from .models import AuditLog

logger = logging.getLogger(__name__)

def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Récupère l'adresse IP du client depuis les headers ou REMOTE_ADDR.
    """
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # En cas de plusieurs IP séparées par des virgules, prendre la première
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
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
            "ip_address": get_client_ip(request) if request else None,
            "user_agent": request.META.get("HTTP_USER_AGENT", "") if request else "",
        }
        return AuditLog.objects.create(**audit_data)
    except Exception as e:
        logger.error(f"Erreur lors de la création du log d’audit: {e}", exc_info=True)
        return None
