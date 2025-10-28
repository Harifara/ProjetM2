import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.cache import cache


class AuthServiceUser:
    """
    ✅ Représente un utilisateur venant du service d'authentification (auth_service)
    """
    def __init__(self, user_data):
        self.id = user_data.get('id') or user_data.get('uuid')  # 🔹 compatibilité UUID
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.full_name = user_data.get('full_name', '')
        self.role = user_data.get('role', 'magasinier')
        self.is_active = user_data.get('is_active', True)
        self.is_authenticated = True

    def __str__(self):
        return self.username or "Utilisateur inconnu"


class AuthServiceAuthentication(BaseAuthentication):
    """
    ✅ Authentifie un utilisateur via le service d’auth (auth_service)
    - Vérifie le token JWT envoyé en header Authorization
    - Fait appel à /api/auth/me/ sur auth_service pour valider
    - Met en cache la réponse 5 min pour éviter trop d’appels réseau
    """

    def authenticate(self, request):
        # 🔹 1. Récupération du header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # → pas de token = pas d'auth (la permission DRF tranchera ensuite)

        token = auth_header.split(' ', 1)[1].strip()
        cache_key = f'auth_user_{token[:20]}'

        # 🔹 2. Vérifie le cache pour éviter un appel réseau
        cached_user = cache.get(cache_key)
        if cached_user:
            return (AuthServiceUser(cached_user), token)

        # 🔹 3. Contacte le service Auth
        try:
            auth_url = f"{settings.AUTH_SERVICE_URL.rstrip('/')}/api/auth/me/"
            response = requests.get(
                auth_url,
                headers={'Authorization': f'Bearer {token}'},
                timeout=getattr(settings, 'AUTH_SERVICE_TIMEOUT', 5)
            )

            if response.status_code == 200:
                user_data = response.json()
                cache.set(cache_key, user_data, timeout=300)  # 5 min
                return (AuthServiceUser(user_data), token)

            elif response.status_code in (401, 403):
                raise AuthenticationFailed('Token invalide ou expiré.')

            else:
                raise AuthenticationFailed(
                    f"Erreur inattendue du service d’authentification ({response.status_code})."
                )

        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed(
                f"Erreur de communication avec le service d’authentification : {str(e)}"
            )

    def authenticate_header(self, request):
        return 'Bearer'
