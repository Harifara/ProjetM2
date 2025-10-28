from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime

from .models import (
    DecashmentRequest, Document, Expense, Payment,
    Budget, Notification, AuditLog
)
from .serializers import (
    DecashmentRequestSerializer, DecashmentRequestCreateSerializer,
    DecashmentRequestUpdateSerializer, DocumentSerializer,
    ExpenseSerializer, ExpenseCreateSerializer,
    PaymentSerializer, PaymentCreateSerializer,
    BudgetSerializer, BudgetCreateSerializer,
    NotificationSerializer, AuditLogSerializer
)
from .permissions import (
    IsFinanceResponsable, IsCoordinateur,
    IsFinanceResponsableOrCoordinateur, IsFinanceResponsableOrReadOnly
)
from .utils import log_audit, create_notification, notify_service, validate_budget


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "ok", "service": "finance"})


class DecashmentRequestViewSet(viewsets.ModelViewSet):
    queryset = DecashmentRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DecashmentRequestCreateSerializer
        elif self.action in ['update', 'partial_update', 'validate', 'reject']:
            return DecashmentRequestUpdateSerializer
        return DecashmentRequestSerializer

    def get_queryset(self):
        queryset = DecashmentRequest.objects.all()
        user_role = self.request.user.get('role')

        if user_role not in ['responsable_finance', 'coordinateur', 'admin']:
            queryset = queryset.filter(requested_by=self.request.user.get('id'))

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        source_service = self.request.query_params.get('source_service')
        if source_service:
            queryset = queryset.filter(source_service=source_service)

        return queryset

    def perform_create(self, serializer):
        decashment = serializer.save(requested_by=self.request.user.get('id'))

        log_audit(
            user_id=self.request.user.get('id'),
            action_type='CREATE_DECASHMENT_REQUEST',
            entity_type='DecashmentRequest',
            entity_id=str(decashment.id),
            details={'amount': str(decashment.amount), 'source': decashment.source_service},
            request=self.request
        )

        create_notification(
            recipient_id=self.request.user.get('id'),
            message=f"Votre demande de décaissement de {decashment.amount} a été créée.",
            notification_type='DECASHMENT_CREATED',
            related_entity_type='DecashmentRequest',
            related_entity_id=decashment.id
        )

    @action(detail=True, methods=['post'], permission_classes=[IsCoordinateur])
    def validate(self, request, pk=None):
        decashment = self.get_object()

        if decashment.status != 'pending':
            return Response(
                {'error': 'Seules les demandes en attente peuvent être validées.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        decashment.status = 'validated'
        decashment.validated_by = request.user.get('id')
        decashment.validated_at = timezone.now()
        decashment.save()

        log_audit(
            user_id=request.user.get('id'),
            action_type='VALIDATE_DECASHMENT',
            entity_type='DecashmentRequest',
            entity_id=str(decashment.id),
            details={'amount': str(decashment.amount)},
            request=request
        )

        create_notification(
            recipient_id=decashment.requested_by,
            message=f"Votre demande de décaissement de {decashment.amount} a été validée.",
            notification_type='DECASHMENT_VALIDATED',
            related_entity_type='DecashmentRequest',
            related_entity_id=decashment.id
        )

        return Response(DecashmentRequestSerializer(decashment).data)

    @action(detail=True, methods=['post'], permission_classes=[IsCoordinateur])
    def reject(self, request, pk=None):
        decashment = self.get_object()
        rejection_reason = request.data.get('rejection_reason')

        if not rejection_reason:
            return Response(
                {'error': 'La raison du rejet est obligatoire.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if decashment.status != 'pending':
            return Response(
                {'error': 'Seules les demandes en attente peuvent être rejetées.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        decashment.status = 'rejected'
        decashment.rejection_reason = rejection_reason
        decashment.validated_by = request.user.get('id')
        decashment.validated_at = timezone.now()
        decashment.save()

        log_audit(
            user_id=request.user.get('id'),
            action_type='REJECT_DECASHMENT',
            entity_type='DecashmentRequest',
            entity_id=str(decashment.id),
            details={'reason': rejection_reason},
            request=request
        )

        create_notification(
            recipient_id=decashment.requested_by,
            message=f"Votre demande de décaissement a été rejetée: {rejection_reason}",
            notification_type='DECASHMENT_REJECTED',
            related_entity_type='DecashmentRequest',
            related_entity_id=decashment.id
        )

        if decashment.source_service and decashment.related_request_id:
            notify_service(
                decashment.source_service,
                f'/api/{decashment.source_service}/notifications/',
                {
                    'message': f"Demande de décaissement rejetée: {rejection_reason}",
                    'related_id': str(decashment.related_request_id)
                }
            )

        return Response(DecashmentRequestSerializer(decashment).data)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, IsFinanceResponsableOrReadOnly]

    def perform_create(self, serializer):
        document = serializer.save(uploaded_by=self.request.user.get('id'))

        log_audit(
            user_id=self.request.user.get('id'),
            action_type='UPLOAD_DOCUMENT',
            entity_type='Document',
            entity_id=str(document.id),
            details={'type': document.document_type, 'name': document.file_name},
            request=self.request
        )


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated, IsFinanceResponsable]

    def get_serializer_class(self):
        if self.action == 'create':
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def perform_create(self, serializer):
        expense = serializer.save(requested_by=self.request.user.get('id'))

        log_audit(
            user_id=self.request.user.get('id'),
            action_type='CREATE_EXPENSE',
            entity_type='Expense',
            entity_id=str(expense.id),
            details={'amount': str(expense.amount), 'type': expense.expense_type},
            request=self.request
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        expense = self.get_object()

        if expense.status != 'pending':
            return Response(
                {'error': 'Seules les dépenses en attente peuvent être approuvées.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        expense.status = 'approved'
        expense.approved_by = request.user.get('id')
        expense.date_approved = timezone.now()
        expense.save()

        log_audit(
            user_id=request.user.get('id'),
            action_type='APPROVE_EXPENSE',
            entity_type='Expense',
            entity_id=str(expense.id),
            details={'amount': str(expense.amount)},
            request=request
        )

        return Response(ExpenseSerializer(expense).data)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        expense = self.get_object()

        if expense.status != 'approved':
            return Response(
                {'error': 'Seules les dépenses approuvées peuvent être exécutées.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        expense.status = 'paid'
        expense.executed_by = request.user.get('id')
        expense.date_paid = timezone.now()
        expense.save()

        log_audit(
            user_id=request.user.get('id'),
            action_type='EXECUTE_EXPENSE',
            entity_type='Expense',
            entity_id=str(expense.id),
            details={'amount': str(expense.amount)},
            request=request
        )

        create_notification(
            recipient_id=expense.requested_by,
            message=f"La dépense de {expense.amount} a été payée.",
            notification_type='EXPENSE_PAID',
            related_entity_type='Expense',
            related_entity_id=expense.id
        )

        return Response(ExpenseSerializer(expense).data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, IsFinanceResponsable]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save(executed_by=self.request.user.get('id'))

        log_audit(
            user_id=self.request.user.get('id'),
            action_type='CREATE_PAYMENT',
            entity_type='Payment',
            entity_id=str(payment.id),
            details={
                'amount': str(payment.amount),
                'method': payment.payment_method,
                'recipient': payment.recipient_name
            },
            request=self.request
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        payment = self.get_object()

        if payment.status == 'completed':
            return Response(
                {'error': 'Ce paiement est déjà complété.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()

        if payment.expense:
            payment.expense.status = 'paid'
            payment.expense.date_paid = timezone.now()
            payment.expense.save()

        log_audit(
            user_id=request.user.get('id'),
            action_type='COMPLETE_PAYMENT',
            entity_type='Payment',
            entity_id=str(payment.id),
            details={'amount': str(payment.amount)},
            request=request
        )

        return Response(PaymentSerializer(payment).data)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    permission_classes = [IsAuthenticated, IsFinanceResponsableOrCoordinateur]

    def get_serializer_class(self):
        if self.action == 'create':
            return BudgetCreateSerializer
        return BudgetSerializer

    def perform_create(self, serializer):
        budget = serializer.save(created_by=self.request.user.get('id'))

        log_audit(
            user_id=self.request.user.get('id'),
            action_type='CREATE_BUDGET',
            entity_type='Budget',
            entity_id=str(budget.id),
            details={
                'department': budget.department,
                'category': budget.category,
                'amount': str(budget.allocated_amount)
            },
            request=self.request
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        fiscal_year = request.query_params.get('fiscal_year', datetime.now().year)
        department = request.query_params.get('department')

        budgets = Budget.objects.filter(fiscal_year=fiscal_year)
        if department:
            budgets = budgets.filter(department=department)

        summary_data = {
            'fiscal_year': fiscal_year,
            'total_allocated': sum(b.allocated_amount for b in budgets),
            'total_spent': sum(b.spent_amount for b in budgets),
            'by_department': {}
        }

        for dept in ['rh', 'stock', 'finance', 'general']:
            dept_budgets = budgets.filter(department=dept)
            summary_data['by_department'][dept] = {
                'allocated': sum(b.allocated_amount for b in dept_budgets),
                'spent': sum(b.spent_amount for b in dept_budgets),
                'remaining': sum(b.remaining_amount for b in dept_budgets)
            }

        return Response(summary_data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient_id=self.request.user.get('id'))

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(
            recipient_id=request.user.get('id'),
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'message': 'Toutes les notifications ont été marquées comme lues.'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsFinanceResponsableOrCoordinateur]
    filterset_fields = ['user_id', 'action_type', 'entity_type']
    search_fields = ['action_type', 'entity_type', 'entity_id']
