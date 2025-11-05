import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from .utils import log_audit

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """
    🧾 Middleware d'audit automatique
    
    🔹 Objectif :
        - Journaliser automatiquement les actions HTTP critiques (POST, PUT, PATCH, DELETE)
        - Enregistrer qui a fait quoi, quand, sur quelle URL et avec quelles données.

    🔹 Exemple d’entrée créée dans AuditLog :
        {
            "user_id": 3,
            "action_type": "API_CREATE",
            "entity_type": "API",
            "entity_id": "/api/auth/users/",
            "details": {"method": "POST", "status_code": 201, "body": {...}},
            "timestamp": "2025-10-15T11:25:00Z"
        }
    """

    def process_response(self, request, response):
        try:
            user = getattr(request, "user", None)

            # 🚫 Ignore si utilisateur non authentifié
            if not (user and user.is_authenticated):
                return response

            # 🚫 Ignore certaines URLs (endpoints non pertinents)
            ignored_prefixes = (
                "/api/auth/health",
                "/api/auth/verify",
                "/admin",
                "/static",
                "/media",
            )
            if request.path.startswith(ignored_prefixes):
                return response

            # ✅ Ne journalise que les requêtes modifiant les données
            if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
                action_map = {
                    "POST": "CREATE",
                    "PUT": "UPDATE",
                    "PATCH": "PARTIAL_UPDATE",
                    "DELETE": "DELETE",
                }
                action_type = f"API_{action_map.get(request.method, 'ACTION')}"

                # 🔍 Extraction du corps JSON, si applicable
                body = {}
                if request.method != "DELETE" and request.content_type == "application/json":
                    try:
                        body = json.loads(request.body.decode("utf-8")) if request.body else {}
                    except Exception as parse_error:
                        logger.warning(f"[AuditLogMiddleware] Erreur parsing JSON : {parse_error}")

                # 🧩 Détails enrichis pour audit
                details = {
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "body": body,
                    "timestamp": now().isoformat(),
                }

                # 🕵️‍♂️ Enregistre l’action d’audit
                log_audit(
                    user=user,
                    action_type=action_type,
                    entity_type="API",
                    entity_id=request.path,
                    details=details,
                    request=request,
                )

        except Exception as e:
            # ⚠️ Ne bloque jamais la requête principale
            logger.error(f"[AuditLogMiddleware] Erreur lors de l’audit : {e}")

        return response
