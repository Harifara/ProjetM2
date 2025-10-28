from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.contrib.auth import logout
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

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


# ==========================================================
# ✅ SERVICE HEALTH CHECK
# ==========================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Vérifie si le service d’auth est en ligne"""
    return Response({"status": "ok"})


# ==========================================================
# ✅ VERIFY TOKEN (utilisé par Kong / Nginx auth_request)
# ==========================================================
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """Vérifie la validité d’un token JWT"""
    if request.method == 'POST':
        token = request.data.get('token')
    else:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(" ")[1]

    try:
        UntypedToken(token)
        return Response({"message": "Token valid"}, status=status.HTTP_200_OK)
    except (InvalidToken, TokenError):
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)


# ==========================================================
# 🔔 NOTIFICATIONS
# ==========================================================
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Marque une notification comme lue"""
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"status": "read"}, status=status.HTTP_200_OK)


# ==========================================================
# 🔐 AUTHENTIFICATION (LOGIN / LOGOUT / ME)
# ==========================================================
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]  # ✅ accepte JSON + form-data

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """Connexion utilisateur (accepte JSON ou form-data)"""
        print("🔍 request.content_type =", request.content_type)
        print("🔍 request.data =", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        # ✅ Journaliser le login
        log_audit(
            user=user,
            action_type="LOGIN",
            details={"status": "SUCCESS"},
            request=request
        )

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Déconnexion utilisateur"""
        log_audit(
            user=request.user,
            action_type='LOGOUT',
            details={},
            request=request
        )
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retourne les infos de l'utilisateur connecté"""
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        """Créer un nouvel utilisateur (inscription)"""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        log_audit(
            user=user,  # l’utilisateur qui vient de s’enregistrer
            action_type="REGISTER",
            entity_type="User",
            entity_id=str(user.id),
            details={"username": user.username, "email": user.email},
            request=request
        )
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


# ==========================================================
# 👥 UTILISATEURS
# ==========================================================
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
            request=self.request
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_audit(
            user=self.request.user,
            action_type='UPDATE_USER',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username},
            request=self.request
        )

    def perform_destroy(self, instance):
        log_audit(
            user=self.request.user,
            action_type='DELETE_USER',
            entity_type='User',
            entity_id=str(instance.id),
            details={'username': instance.username},
            request=self.request
        )
        instance.delete()

    @action(detail=True, methods=['post'], url_path='change-password',
            permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def change_password(self, request, pk=None):
        """Changer le mot de passe d’un utilisateur"""
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
            request=request
        )

        return Response({'message': 'Mot de passe modifié avec succès.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
        """Activer / désactiver un utilisateur"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        log_audit(
            user=request.user,
            action_type='TOGGLE_USER_STATUS',
            entity_type='User',
            entity_id=str(user.id),
            details={'username': user.username, 'is_active': user.is_active},
            request=request
        )

        return Response({
            'message': f'Utilisateur {"activé" if user.is_active else "désactivé"}.'
        }, status=status.HTTP_200_OK)


# ==========================================================
# 🧾 JOURNAUX D’AUDIT
# ==========================================================
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API read-only pour les journaux d'audit"""
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
        """Retourne les 20 derniers journaux de l'utilisateur connecté"""
        logs = self.get_queryset().filter(user=request.user)[:20]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================================
# 🎟️ TOKEN JWT PERSONNALISÉ
# ==========================================================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
