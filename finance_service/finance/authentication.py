from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings
import requests


class JWTAuthenticationFromAuthService(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user_from_auth_service(validated_token)

        return (user, validated_token)

    def get_user_from_auth_service(self, validated_token):
        try:
            auth_service_url = settings.AUTH_SERVICE_URL
            headers = {
                'Authorization': f'Bearer {str(validated_token)}'
            }
            response = requests.get(
                f'{auth_service_url}/api/auth/me/',
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                user_data = response.json()
                return user_data
            else:
                raise InvalidToken('Impossible de valider le token auprès du service d\'authentification')

        except requests.RequestException:
            raise InvalidToken('Erreur de communication avec le service d\'authentification')
