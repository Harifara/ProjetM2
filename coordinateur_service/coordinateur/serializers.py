from rest_framework import serializers
from .models import DecashmentValidation, AuditLog, OperationView

class DecashmentValidationSerializer(serializers.ModelSerializer):
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    validation_status_display = serializers.CharField(source='get_validation_status_display', read_only=True)

    class Meta:
        model = DecashmentValidation
        fields = [
            'id', 'request_type', 'request_type_display', 'request_id',
            'validation_status', 'validation_status_display', 'validated_by',
            'validation_date', 'comments', 'amount', 'reason', 'requested_by',
            'department', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DecashmentValidationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecashmentValidation
        fields = [
            'request_type', 'request_id', 'amount', 'reason',
            'requested_by', 'department'
        ]

class ValidateDecashmentSerializer(serializers.Serializer):
    validation_status = serializers.ChoiceField(choices=['validé', 'rejeté'])
    comments = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['validation_status'] == 'rejeté' and not attrs.get('comments'):
            raise serializers.ValidationError({
                "comments": "Un commentaire est requis pour le rejet."
            })
        return attrs

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_id', 'action_type', 'entity_type', 'entity_id',
            'timestamp', 'details', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']

class OperationViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationView
        fields = ['id', 'viewed_by', 'operation_type', 'operation_id', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']

class DashboardStatsSerializer(serializers.Serializer):
    total_pending = serializers.IntegerField()
    total_validated = serializers.IntegerField()
    total_rejected = serializers.IntegerField()
    pending_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    validated_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    rejected_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    by_request_type = serializers.DictField()
