import jwt
from datetime import datetime, timedelta
from decouple import config

SECRET_KEY = config("JWT_SECRET", default="my_super_secret_key_123")
ISSUER = "auth-service"

def generate_kong_jwt(user_id):
    payload = {
        "sub": str(user_id),
        "iss": ISSUER,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
