import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class KongJWTUser:
    def __init__(self, user_id, username, payload):
        self.id = user_id
        self.username = username
        self.payload = payload
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def __str__(self):
        return self.username


class KongJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
                issuer=settings.JWT_ISSUER
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expiré')
        except jwt.InvalidIssuerError:
            raise exceptions.AuthenticationFailed('Émetteur de token invalide')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token invalide')

        user_id = payload.get('sub')
        username = payload.get('username', f'user_{user_id}')

        if not user_id:
            raise exceptions.AuthenticationFailed('Token invalide: sub manquant')

        user = KongJWTUser(user_id=user_id, username=username, payload=payload)

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'
