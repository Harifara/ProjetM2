# finance/utils.py
import jwt
import time
from django.conf import settings

def generate_service_token():
    """
    Génère un JWT signé pour que Finance puisse appeler d'autres services
    """
    payload = {
        "iss": "finance_service",      # identifiant du service
        "iat": int(time.time()),       # issued at
        "exp": int(time.time()) + 60,  # expire dans 60 secondes
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token
