from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import DecashmentValidation, AuditLog, OperationView
from .serializers import (
    DecashmentValidationSerializer,
    DecashmentValidationCreateSerializer,
    ValidateDecashmentSerializer,
    AuditLogSerializer,
    OperationViewSerializer,
    DashboardStatsSerializer
)
from .permissions import IsCoordinateur
from .utils import log_audit

from django.http import JsonResponse

def health_view(request):
    return JsonResponse({"status": "ok"})


class DecashmentValidationViewSet(viewsets.ModelViewSet):
    queryset = DecashmentValidation.objects.all()
    permission_classes = [IsAuthenticated, IsCoordinateur]

    def get_serializer_class(self):
        if self.action == 'create':
            return DecashmentValidationCreateSerializer
        elif self.action == 'validate':
            return ValidateDecashmentSerializer
        return DecashmentValidationSerializer

    def perform_create(self, serializer):
        validation = serializer.save()
        log_audit(
            user_id=self.request.user_id,
            action_type='CREATE_DECASHMENT_REQUEST',
            entity_type='DecashmentValidation',
            entity_id=str(validation.id),
            details={
                'request_type': validation.request_type,
                'amount': str(validation.amount) if validation.amount else None
            },
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='validate')
    def validate(self, request, pk=None):
        validation = self.get_object()

        if validation.validation_status != 'en_attente':
            return Response(
                {'error': 'Cette demande a déjà été traitée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ValidateDecashmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validation.validation_status = serializer.validated_data['validation_status']
        validation.comments = serializer.validated_data.get('comments', '')
        validation.validated_by = request.user_id
        validation.validation_date = timezone.now()
        validation.save()

        log_audit(
            user_id=request.user_id,
            action_type=f'{"VALIDATE" if validation.validation_status == "validé" else "REJECT"}_DECASHMENT',
            entity_type='DecashmentValidation',
            entity_id=str(validation.id),
            details={
                'validation_status': validation.validation_status,
                'comments': validation.comments,
                'request_type': validation.request_type
            },
            request=request
        )

        return Response(
            DecashmentValidationSerializer(validation).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        pending_validations = self.queryset.filter(validation_status='en_attente')
        page = self.paginate_queryset(pending_validations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(pending_validations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='validated')
    def validated(self, request):
        validated = self.queryset.filter(validation_status='validé')
        page = self.paginate_queryset(validated)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(validated, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='rejected')
    def rejected(self, request):
        rejected = self.queryset.filter(validation_status='rejeté')
        page = self.paginate_queryset(rejected)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(rejected, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        stats = {
            'total_pending': self.queryset.filter(validation_status='en_attente').count(),
            'total_validated': self.queryset.filter(validation_status='validé').count(),
            'total_rejected': self.queryset.filter(validation_status='rejeté').count(),
        }

        stats['pending_amount'] = self.queryset.filter(
            validation_status='en_attente'
        ).aggregate(total=Sum('amount'))['total'] or 0

        stats['validated_amount'] = self.queryset.filter(
            validation_status='validé'
        ).aggregate(total=Sum('amount'))['total'] or 0

        stats['rejected_amount'] = self.queryset.filter(
            validation_status='rejeté'
        ).aggregate(total=Sum('amount'))['total'] or 0

        by_type = {}
        for request_type in ['purchase', 'payment', 'decashment', 'stock_transfer']:
            by_type[request_type] = {
                'pending': self.queryset.filter(
                    request_type=request_type,
                    validation_status='en_attente'
                ).count(),
                'validated': self.queryset.filter(
                    request_type=request_type,
                    validation_status='validé'
                ).count(),
                'rejected': self.queryset.filter(
                    request_type=request_type,
                    validation_status='rejeté'
                ).count(),
            }

        stats['by_request_type'] = by_type

        serializer = DashboardStatsSerializer(data=stats)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class OperationViewViewSet(viewsets.ModelViewSet):
    queryset = OperationView.objects.all()
    serializer_class = OperationViewSerializer
    permission_classes = [IsAuthenticated, IsCoordinateur]

    def perform_create(self, serializer):
        view = serializer.save(viewed_by=self.request.user_id)
        log_audit(
            user_id=self.request.user_id,
            action_type='CONSULT_OPERATION',
            entity_type=view.operation_type,
            entity_id=str(view.operation_id),
            details={'operation_type': view.operation_type},
            request=self.request
        )

    @action(detail=False, methods=['get'], url_path='my-views')
    def my_views(self, request):
        my_views = self.queryset.filter(viewed_by=request.user_id)
        page = self.paginate_queryset(my_views)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(my_views, many=True)
        return Response(serializer.data)

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsCoordinateur]
    filterset_fields = ['user_id', 'action_type', 'entity_type']
    search_fields = ['action_type', 'entity_type', 'entity_id']
