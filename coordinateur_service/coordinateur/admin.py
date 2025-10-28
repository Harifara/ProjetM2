from django.contrib import admin
from .models import DecashmentValidation, AuditLog, OperationView

@admin.register(DecashmentValidation)
class DecashmentValidationAdmin(admin.ModelAdmin):
    list_display = [
        'request_type', 'validation_status', 'amount',
        'requested_by', 'validated_by', 'created_at'
    ]
    list_filter = ['request_type', 'validation_status', 'created_at', 'department']
    search_fields = ['request_id', 'requested_by', 'reason', 'comments']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Informations de la demande', {
            'fields': ('request_type', 'request_id', 'requested_by', 'department')
        }),
        ('Détails financiers', {
            'fields': ('amount', 'reason')
        }),
        ('Validation', {
            'fields': ('validation_status', 'validated_by', 'validation_date', 'comments')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'user_id', 'entity_type', 'entity_id', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'entity_type', 'timestamp']
    search_fields = ['action_type', 'entity_type', 'entity_id', 'user_id']
    readonly_fields = ['user_id', 'action_type', 'entity_type', 'entity_id', 'timestamp', 'details', 'ip_address', 'user_agent']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(OperationView)
class OperationViewAdmin(admin.ModelAdmin):
    list_display = ['operation_type', 'viewed_by', 'operation_id', 'viewed_at']
    list_filter = ['operation_type', 'viewed_at']
    search_fields = ['operation_type', 'operation_id', 'viewed_by']
    readonly_fields = ['viewed_at']
    ordering = ['-viewed_at']
