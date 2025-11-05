from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DistrictViewSet, CommuneViewSet, FokontanyViewSet,
    DepartmentViewSet, FunctionViewSet, ContractViewSet,
    EmployeeViewSet, AssignmentViewSet, CVViewSet,
    LeaveTypeViewSet, LeaveRequestViewSet,
    PayslipViewSet, PaymentRequestViewSet
)

# ==================== ROUTEUR ====================
router = DefaultRouter()

# -------------------- Géographie --------------------
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'communes', CommuneViewSet, basename='commune')
router.register(r'fokontanys', FokontanyViewSet, basename='fokontany')

# -------------------- Ressources humaines --------------------
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'functions', FunctionViewSet, basename='function')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'assignments', AssignmentViewSet, basename='assignment')

# -------------------- CV --------------------
router.register(r'cvs', CVViewSet, basename='cv')

# -------------------- Congés --------------------
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')

# -------------------- Bulletins de paie --------------------
router.register(r'payslips', PayslipViewSet, basename='payslip')

# -------------------- Demandes de paiement --------------------
router.register(r'payment-requests', PaymentRequestViewSet, basename='payment-request')


# ==================== INCLUSION DES ROUTES ====================
urlpatterns = [
    # Toutes les routes sont protégées par KongJWTAuthentication via les ViewSets
    path('', include(router.urls)),
]
