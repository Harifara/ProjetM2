from rest_framework import serializers
from .models import (
    DecashmentRequest, Document, Expense, Payment,
    Budget, Notification, AuditLog
)


class DecashmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecashmentRequest
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'validated_by', 'validated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        return value


class DecashmentRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecashmentRequest
        fields = [
            'source_service', 'amount', 'reason',
            'related_request_type', 'related_request_id'
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à zéro.")
        return value


class DecashmentRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecashmentRequest
        fields = ['status', 'rejection_reason']

    def validate(self, attrs):
        if attrs.get('status') == 'rejected' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({
                "rejection_reason": "La raison du rejet est obligatoire."
            })
        return attrs


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'uploaded_by']


class ExpenseSerializer(serializers.ModelSerializer):
    document_details = DocumentSerializer(source='document', read_only=True)
    decashment_details = DecashmentRequestSerializer(source='decashment_request', read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = [
            'id', 'date_requested', 'date_approved', 'date_paid',
            'approved_by', 'executed_by'
        ]


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'amount', 'expense_type', 'description',
            'related_request_id', 'decashment_request', 'notes'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    expense_details = ExpenseSerializer(source='expense', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'executed_at', 'completed_at', 'executed_by']


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'expense', 'payment_method', 'amount', 'recipient_name',
            'recipient_account', 'reference_number', 'notes'
        ]


class BudgetSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.ReadOnlyField()
    utilization_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'spent_amount', 'created_by']


class BudgetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = [
            'department', 'category', 'allocated_amount',
            'fiscal_year', 'month'
        ]

    def validate_allocated_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant alloué doit être supérieur à zéro.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'read_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']
