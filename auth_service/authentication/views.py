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
from decouple import config

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
from .models import User, AuditLog, Notification
from .permissions import IsAdmin, IsOwnerOrAdmin
from .utils import log_audit

# ==========================
# 🔹 Health check
# ==========================
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


# ==========================
# 🔹 Verify token
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
# 🔹 Kong Token (JWT pour Kong Gateway)
# ==========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def kong_token(request):
    """
    Génère un JWT valide pour Kong Gateway
    """
    secret = config("KONG_JWT_SECRET", default="my_super_secret_key_123")
    payload = {
        "iss": "auth-service",
        "sub": str(request.user.id),
        "username": request.user.username,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

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

        # Génération du token pour Kong
        secret = config("KONG_JWT_SECRET", default="my_super_secret_key_123")
        payload = {
            "iss": "auth-service",
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
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
        user = serializer.save()
        log_audit(
            user=user,
            action_type="REGISTER",
            entity_type="User",
            entity_id=str(user.id),
            details={"username": user.username, "email": user.email},
            request=request,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], url_path='update', permission_classes=[IsAuthenticated])
    def update_user(self, request, pk=None):
        """
        Met à jour un utilisateur (PATCH)
        """
        user = self.get_object()  # récupère l'utilisateur ciblé par l'URL
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        # Log audit
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
# 🔹 Users
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

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit(
            user=self.request.user,
            action_type='CREATE_USER',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username, 'role': user.role},
            request=self.request,
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_audit(
            user=self.request.user,
            action_type='UPDATE_USER',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username},
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
# 🔹 Audit logs
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
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        return queryset

    @action(detail=False, methods=['get'], url_path='my-logs')
    def my_logs(self, request):
        logs = self.get_queryset().filter(user=request.user)[:20]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


# ==========================
# 🔹 JWT custom view
# ==========================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
