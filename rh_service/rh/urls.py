from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter

from .views import (
    DistrictViewSet,
    CommuneViewSet,
    FokontanyViewSet,
    EmployeeViewSet,
    ContractViewSet,
    LeaveRequestViewSet,
    AssignmentViewSet,
    PaymentRequestViewSet,
    PurchaseRequestViewSet,
    AuditLogViewSet,
    test_auth
)

# -------------------------
# Health check
# -------------------------
def health(request):
    return JsonResponse({"status": "ok", "service": "rh_service"})

# -------------------------
# Router
# -------------------------
router = DefaultRouter()
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'communes', CommuneViewSet, basename='commune')
router.register(r'fokontany', FokontanyViewSet, basename='fokontany')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'payment-requests', PaymentRequestViewSet, basename='payment-request')
router.register(r'purchase-requests', PurchaseRequestViewSet, basename='purchase-request')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

# -------------------------
# URL Patterns
# -------------------------
urlpatterns = [
    path('', include(router.urls)),
    path('health/', health, name='health'),
    path('test-auth/', test_auth, name='test-auth'),
]
