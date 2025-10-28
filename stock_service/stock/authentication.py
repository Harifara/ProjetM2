# stock/authentication.py
import requests
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework import exceptions


class AuthServiceJWTAuthentication(JWTAuthentication):
    """
    Authentication class that:
      - tente d'abord de valider le token localement (AccessToken)
      - si AUTH_SERVICE_URL est configuré et la validation locale échoue, appelle le service d'auth (remote verify)
    Remplit request._auth_user_data (dict) pour que views/middleware puissent l'utiliser.
    Retourne (user, token) où user est AnonymousUser() (on ne maintient pas les users locaux).
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        # Essaie la validation locale (décodage simplejwt)
        try:
            validated_token = self.get_validated_token(raw_token)
            # get payload-like dict
            payload = validated_token.payload if hasattr(validated_token, 'payload') else dict(validated_token)
            # Remplir user_data
            request.user_id = payload.get('user_id') or payload.get('sub')  # selon ton payload
            request.user_data = {
                'id': request.user_id,
                'role': payload.get('role', ''),
                'username': payload.get('username', payload.get('email', ''))
            }
            # Retourne un user factice + token pour DRF
            return (AnonymousUser(), validated_token)
        except TokenError:
            # Si AUTH_SERVICE_URL est configuré, essaie la vérification distante
            auth_url = getattr(settings, 'AUTH_SERVICE_URL', None)
            if not auth_url:
                # token invalide et pas d'auth service => échec
                raise exceptions.AuthenticationFailed('Token invalide')

            verify_url = auth_url.rstrip('/') + '/verify/'  # => ex: http://auth_service:8000/api/auth/verify/
            try:
                resp = requests.get(verify_url, headers={'Authorization': f'Bearer {raw_token}'}, timeout=5)
            except requests.RequestException:
                raise exceptions.AuthenticationFailed('Impossible de joindre le service d\'authentification')

            if resp.status_code == 200:
                data = resp.json()
                # Attends que l'auth service renvoie user info: id, role, username...
                request.user_id = data.get('id') or data.get('user_id')
                request.user_data = {
                    'id': request.user_id,
                    'role': data.get('role', ''),
                    'username': data.get('username', data.get('email', ''))
                }
                # renvoie user factice + token string
                return (AnonymousUser(), raw_token)
            else:
                raise exceptions.AuthenticationFailed('Token non valide (auth service)')
