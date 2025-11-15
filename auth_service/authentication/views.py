from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.contrib.auth import logout
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
import jwt
import uuid
from decouple import config
from rest_framework.views import APIView


from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    AuditLogSerializer,
    NotificationSerializer,
)
from .models import User, AuditLog, Notification, UserRole
from .permissions import IsAdmin, IsOwnerOrAdmin
from .utils import log_audit


# ==========================
# 🔹 Health Check
# ==========================
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


# ==========================
# 🔹 Verify JWT Token
# ==========================
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_token(request):
    token = (
        request.data.get('token')
        if request.method == 'POST'
        else request.headers.get('Authorization', '').split(" ")[1]
        if request.headers.get('Authorization', '').startswith("Bearer ")
        else None
    )
    if not token:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        UntypedToken(token)
        return Response({"message": "Token valid"}, status=status.HTTP_200_OK)
    except (InvalidToken, TokenError):
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)


# ==========================
# 🔹 Kong JWT Token
# ==========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def kong_token(request):
    """
    Génère un JWT compatible avec Kong Gateway
    """
    user = request.user
    secret = config("KONG_JWT_SECRET", default="my_super_secret_key_123")

    payload = {
        "iss": "auth-service",
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    if user.role == UserRole.MAGASINIER and user.magasin_id:
        payload["magasin_id"] = str(user.magasin_id)

    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return Response({"kong_token": token})


# ==========================
# 🔹 Notifications
# ==========================
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"status": "read"}, status=status.HTTP_200_OK)


# ==========================
# 🔹 Authentification principale
# ==========================
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    # --- Login ---
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Génération du token Kong
        secret = config("KONG_JWT_SECRET", default="my_super_secret_key_123")
        payload = {
            "iss": "auth-service",
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        if user.role == UserRole.MAGASINIER and user.magasin_id:
            payload["magasin_id"] = str(user.magasin_id)

        kong_token = jwt.encode(payload, secret, algorithm="HS256")
        if isinstance(kong_token, bytes):
            kong_token = kong_token.decode("utf-8")

        log_audit(user=user, action_type="LOGIN", details={"status": "SUCCESS"}, request=request)
        return Response({
            'refresh': str(refresh),
            'access': str(access),
            'kong_token': kong_token,
            'user': UserSerializer(user).data
        })

    # --- Logout ---
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        log_audit(user=request.user, action_type='LOGOUT', details={}, request=request)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # --- Infos utilisateur connecté ---
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    # --- Register ---
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data.get('role')
        magasin_id = serializer.validated_data.get('magasin_id')

        if role == UserRole.MAGASINIER:
            if not magasin_id:
                return Response({"magasin_id": "Le magasin est requis pour un magasinier."}, status=400)
            if User.objects.filter(magasin_id=magasin_id).exists():
                return Response({"magasin_id": "Ce magasin est déjà assigné à un autre magasinier."}, status=400)

        user = serializer.save()
        log_audit(
            user=user,
            action_type="REGISTER",
            entity_type="User",
            entity_id=str(user.id),
            details={"username": user.username, "email": user.email, "magasin_id": str(user.magasin_id) if user.magasin_id else None},
            request=request,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    # --- Update utilisateur ---
    @action(detail=True, methods=['patch'], url_path='update', permission_classes=[IsAuthenticated])
    def update_user(self, request, pk=None):
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        magasin_id = request.data.get('magasin_id')
        role = request.data.get('role', user.role)
        if role == UserRole.MAGASINIER and magasin_id:
            if User.objects.filter(magasin_id=magasin_id).exclude(id=user.id).exists():
                return Response({"magasin_id": "Ce magasin est déjà assigné à un autre magasinier."}, status=400)

        updated_user = serializer.save()

        log_audit(
            user=request.user,
            action_type='UPDATE_USER',
            entity_type='User',
            entity_id=str(updated_user.id),
            details={'updated_fields': serializer.validated_data},
            request=request,
        )

        return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)


# ==========================
# 🔹 Users Management
# ==========================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'full_name']
    ordering_fields = ['created_at', 'username']
    ordering = ['username']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == UserRole.MAGASINIER:
            qs = qs.filter(id=user.id)
        return qs

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit(
            user=self.request.user,
            action_type='CREATE_USER',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username, 'role': user.role, 'magasin_id': str(user.magasin_id) if user.magasin_id else None},
            request=self.request,
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_audit(
            user=self.request.user,
            action_type='UPDATE_USER',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username, 'magasin_id': str(user.magasin_id) if user.magasin_id else None},
            request=self.request,
        )

    def perform_destroy(self, instance):
        log_audit(
            user=self.request.user,
            action_type='DELETE_USER',
            entity_type='User',
            entity_id=str(instance.id),
            details={'username': instance.username},
            request=self.request,
        )
        instance.delete()

    @action(detail=True, methods=['post'], url_path='change-password', permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        log_audit(
            user=request.user,
            action_type='CHANGE_PASSWORD',
            entity_type='User',
            entity_id=str(user.id),
            details={'target_user': user.username},
            request=request,
        )
        return Response({'message': 'Mot de passe modifié avec succès.'})

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        log_audit(
            user=request.user,
            action_type='TOGGLE_USER_STATUS',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username, 'is_active': user.is_active},
            request=request,
        )
        return Response({'message': f'Utilisateur {"activé" if user.is_active else "désactivé"}.'})


# ==========================
# 🔹 Audit Logs
# ==========================
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action_type', 'entity_type']
    search_fields = ['action_type', 'entity_type', 'entity_id', 'ip_address']
    ordering_fields = ['timestamp', 'action_type']
    ordering = ['-timestamp']

    def get_queryset(self):
        user = self.request.user
        queryset = AuditLog.objects.select_related('user').all()
        if user.role == UserRole.MAGASINIER:
            queryset = queryset.filter(user=user)
        return queryset

    @action(detail=False, methods=['get'], url_path='my-logs')
    def my_logs(self, request):
        logs = self.get_queryset().filter(user=request.user)[:20]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


# ==========================
# 🔹 JWT Custom View
# ==========================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])  # Autorise rh_service à envoyer des logs
def receive_external_log(request):
    data = request.data
    try:
        AuditLog.objects.create(
            id=uuid.uuid4(),
            user=None,
            action_type=data.get("action_type"),
            entity_type=data.get("entity_type"),
            entity_id=data.get("entity_id"),
            details=data.get("details", {}),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response({"status": "ok"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

class CombinedLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Logs locaux auth_service
        local_logs = AuditLog.objects.all().order_by('-timestamp')
        local_serialized = AuditLogSerializer(local_logs, many=True).data

        # Optionnel : récupérer les logs RH depuis rh_service
        try:
            response = requests.get("http://rh_service:8000/api/rh/logs/", timeout=5)
            rh_logs = response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Erreur récupération logs RH : {e}")
            rh_logs = []

        all_logs = local_serialized + rh_logs
        all_logs_sorted = sorted(all_logs, key=lambda x: x['timestamp'], reverse=True)
        return Response(all_logs_sorted)