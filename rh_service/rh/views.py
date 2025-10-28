from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    District, Commune, Fokontany, Employee, Contract, LeaveRequest,
    Assignment, PaymentRequest, PurchaseRequest, AuditLog
)
from .serializers import (
    DistrictSerializer, CommuneSerializer, FokontanySerializer, EmployeeSerializer, ContractSerializer,
    LeaveRequestSerializer, LeaveRequestValidationSerializer,
    AssignmentSerializer, AssignmentValidationSerializer,
    PaymentRequestSerializer, PaymentRequestValidationSerializer,
    PurchaseRequestSerializer, PurchaseRequestValidationSerializer,
    AuditLogSerializer, EmployeeStatsSerializer
)
from .permissions import (
    IsResponsableRH, IsResponsableRHOrReadOnly,
    IsEmployeeOwnerOrResponsableRH, CanValidateLeave,
    CanValidateAssignment, CanCreatePaymentRequest
)
from .utils import log_audit, get_user_info

# -------------------------
# Test Auth
# -------------------------
def test_auth(request):
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return JsonResponse({
            "message": "Authentifié avec succès via AuthServiceMiddleware",
            "user": {
                "id": str(user.id),
                "username": user.username,
            }
        })
    return JsonResponse({"error": "Non authentifié"}, status=401)

# -------------------------
# Districts / Communes / Fokontany
# -------------------------
class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated, IsResponsableRHOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'id'

class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer
    permission_classes = [IsAuthenticated, IsResponsableRHOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'id'

class FokontanyViewSet(viewsets.ModelViewSet):
    queryset = Fokontany.objects.all()
    serializer_class = FokontanySerializer
    permission_classes = [IsAuthenticated, IsResponsableRHOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'id'

# -------------------------
# Employee
# -------------------------
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('district').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsEmployeeOwnerOrResponsableRH]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'department', 'district']
    search_fields = ['employee_number', 'position', 'department']
    ordering_fields = ['hire_date', 'created_at', 'employee_number']
    ordering = ['-created_at']
    lookup_field = 'id'

    def perform_create(self, serializer):
        employee = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='CREATE_EMPLOYEE',
            entity_type='Employee',
            entity_id=str(employee.id),
            details={'employee_number': employee.employee_number, 'position': employee.position},
            request=self.request
        )

    def perform_update(self, serializer):
        employee = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='UPDATE_EMPLOYEE',
            entity_type='Employee',
            entity_id=str(employee.id),
            details={'employee_number': employee.employee_number, 'position': employee.position},
            request=self.request
        )

    def perform_destroy(self, instance):
        log_audit(
            user_id=str(self.request.user.id),
            action_type='DELETE_EMPLOYEE',
            entity_type='Employee',
            entity_id=str(instance.id),
            details={'employee_number': instance.employee_number},
            request=self.request
        )
        instance.delete()

    # --- Custom routes ---
    @action(detail=True, methods=['get'], url_path='user')
    def user_info(self, request, id=None):
        employee = self.get_object()
        user_data = get_user_info(employee.user_id)
        return Response(user_data)

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAuthenticated, IsResponsableRH])
    def stats(self, request):
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='active').count()
        on_leave = Employee.objects.filter(status='on_leave').count()
        by_department = dict(Employee.objects.values('department').annotate(count=Count('id')).values_list('department', 'count'))
        by_district = dict(Employee.objects.select_related('district').values('district__name').annotate(count=Count('id')).values_list('district__name', 'count'))
        serializer = EmployeeStatsSerializer({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'on_leave': on_leave,
            'by_department': by_department,
            'by_district': by_district
        })
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='contracts')
    def contracts(self, request, id=None):
        employee = self.get_object()
        serializer = ContractSerializer(employee.contracts.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='leave-requests')
    def leave_requests(self, request, id=None):
        employee = self.get_object()
        serializer = LeaveRequestSerializer(employee.leave_requests.all(), many=True)
        return Response(serializer.data)

# -------------------------
# Contract
# -------------------------
class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('employee', 'employee__district').all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, IsResponsableRH]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'contract_type', 'employee']
    search_fields = ['employee__employee_number', 'contract_type']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    lookup_field = 'id'

    def perform_create(self, serializer):
        contract = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='CREATE_CONTRACT',
            entity_type='Contract',
            entity_id=str(contract.id),
            details={'employee': contract.employee.employee_number, 'contract_type': contract.contract_type},
            request=self.request
        )

    def perform_update(self, serializer):
        contract = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='UPDATE_CONTRACT',
            entity_type='Contract',
            entity_id=str(contract.id),
            details={'employee': contract.employee.employee_number, 'status': contract.status},
            request=self.request
        )

# -------------------------
# LeaveRequest
# -------------------------
class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'leave_type', 'employee']
    search_fields = ['employee__employee_number', 'reason']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        role = getattr(user, "role", None)
        if role in ["responsable_rh", "admin"]:
            return queryset
        try:
            employee = Employee.objects.get(user_id=user.id)
            return queryset.filter(employee=employee)
        except Employee.DoesNotExist:
            return queryset.none()

    def perform_create(self, serializer):
        leave_request = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='CREATE_LEAVE_REQUEST',
            entity_type='LeaveRequest',
            entity_id=str(leave_request.id),
            details={'employee': leave_request.employee.employee_number, 'leave_type': leave_request.leave_type, 'start_date': str(leave_request.start_date), 'end_date': str(leave_request.end_date)},
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='validate', permission_classes=[IsAuthenticated, CanValidateLeave])
    def validate_leave(self, request, id=None):
        leave_request = self.get_object()
        if leave_request.status != 'pending':
            return Response({'error': 'Seules les demandes en attente peuvent être validées.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LeaveRequestValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request.status = serializer.validated_data['status']
        leave_request.validated_by = request.user.id
        leave_request.validated_at = timezone.now()
        if leave_request.status == 'rejected':
            leave_request.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        leave_request.save()
        log_audit(
            user_id=str(request.user.id),
            action_type='VALIDATE_LEAVE_REQUEST',
            entity_type='LeaveRequest',
            entity_id=str(leave_request.id),
            details={'employee': leave_request.employee.employee_number, 'status': leave_request.status, 'rejection_reason': leave_request.rejection_reason},
            request=request
        )
        return Response(LeaveRequestSerializer(leave_request).data)

# -------------------------
# Assignment
# -------------------------
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('employee', 'new_district').all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'employee']
    search_fields = ['employee__employee_number']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    lookup_field = 'id'

    def perform_create(self, serializer):
        assignment = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='CREATE_ASSIGNMENT',
            entity_type='Assignment',
            entity_id=str(assignment.id),
            details={'employee': assignment.employee.employee_number, 'assignment_type': assignment.assignment_type},
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='validate', permission_classes=[IsAuthenticated, CanValidateAssignment])
    def validate_assignment(self, request, id=None):
        assignment = self.get_object()
        if assignment.status != 'pending':
            return Response({'error': 'Seules les affectations en attente peuvent être validées.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AssignmentValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment.status = serializer.validated_data['status']
        assignment.validated_by = request.user.id
        assignment.validated_at = timezone.now()
        assignment.save()
        log_audit(
            user_id=str(request.user.id),
            action_type='VALIDATE_ASSIGNMENT',
            entity_type='Assignment',
            entity_id=str(assignment.id),
            details={'status': assignment.status},
            request=self.request
        )
        return Response(AssignmentSerializer(assignment).data)

# -------------------------
# PaymentRequest
# -------------------------
class PaymentRequestViewSet(viewsets.ModelViewSet):
    queryset = PaymentRequest.objects.select_related('employee').all()
    serializer_class = PaymentRequestSerializer
    permission_classes = [IsAuthenticated, CanCreatePaymentRequest]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'employee']
    search_fields = ['employee__employee_number', 'reason']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_field = 'id'

    def perform_create(self, serializer):
        payment = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='CREATE_PAYMENT_REQUEST',
            entity_type='PaymentRequest',
            entity_id=str(payment.id),
            details={'employee': payment.employee.employee_number if payment.employee else None, 'amount': str(payment.amount)},
            request=self.request
        )

# -------------------------
# PurchaseRequest
# -------------------------
class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated, IsResponsableRH]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['item_description', 'department']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    lookup_field = 'id'

    def perform_create(self, serializer):
        purchase = serializer.save()
        log_audit(
            user_id=str(self.request.user.id),
            action_type='CREATE_PURCHASE_REQUEST',
            entity_type='PurchaseRequest',
            entity_id=str(purchase.id),
            details={'item_description': purchase.item_description[:100]},
            request=self.request
        )

# -------------------------
# AuditLog (read-only)
# -------------------------
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsResponsableRH]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action_type', 'entity_type', 'user_id']
    search_fields = ['details', 'entity_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    lookup_field = 'id'
