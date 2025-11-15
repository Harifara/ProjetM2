import jwt
from datetime import datetime, timedelta
from decouple import config
from .models import UserRole

SECRET_KEY = config("JWT_SECRET", default="my_super_secret_key_123")
ISSUER = "auth-service"

def generate_kong_jwt(user):
    """
    Génère un JWT pour Kong Gateway.
    user : instance de User
    """
    payload = {
        "sub": str(user.id),
        "iss": ISSUER,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    # ⚡ Ajouter store_id si l'utilisateur est magasinier
    if user.role == UserRole.MAGASINIER and hasattr(user, 'store_id') and user.store_id:
        payload["store_id"] = str(user.store_id)

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token
