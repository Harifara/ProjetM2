from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AuthViewSet,
    UserViewSet,
    AuditLogViewSet,
    NotificationViewSet,
    health,
    verify_token,
    CustomTokenObtainPairView,
    kong_token,
)

# ------------------------------------------------------------
# 🚦 Configuration du routeur DRF
# ------------------------------------------------------------
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'logs', AuditLogViewSet, basename='auditlogs')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'', AuthViewSet, basename='auth')  # login, logout, me, register

# ------------------------------------------------------------
# 🌍 URL patterns de l'app "authentication"
# ------------------------------------------------------------
urlpatterns = [
    path('health/', health, name='health'),
    path('verify-token/', verify_token, name='verify_token'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('kong-token/', kong_token, name='kong_token'),
    path('', include(router.urls)),
]
