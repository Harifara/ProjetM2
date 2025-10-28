from django.contrib import admin
from .models import (
    DecashmentRequest, Document, Expense, Payment,
    Budget, Notification, AuditLog
)


@admin.register(DecashmentRequest)
class DecashmentRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'source_service', 'amount', 'status', 'requested_by', 'created_at']
    list_filter = ['status', 'source_service', 'created_at']
    search_fields = ['reason', 'requested_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'document_type', 'file_name', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'created_at']
    search_fields = ['file_name', 'notes']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'expense_type', 'amount', 'status', 'date_requested', 'date_paid']
    list_filter = ['status', 'expense_type', 'date_requested']
    search_fields = ['description']
    readonly_fields = ['date_requested', 'date_approved', 'date_paid']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_method', 'amount', 'recipient_name', 'status', 'executed_at']
    list_filter = ['status', 'payment_method', 'executed_at']
    search_fields = ['recipient_name', 'reference_number']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'department', 'category', 'fiscal_year', 'allocated_amount', 'spent_amount']
    list_filter = ['department', 'fiscal_year', 'month']
    search_fields = ['category']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient_id', 'notification_type', 'is_read', 'created_at']
    list_filter = ['is_read', 'notification_type', 'created_at']
    search_fields = ['message']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'action_type', 'entity_type', 'timestamp']
    list_filter = ['action_type', 'entity_type', 'timestamp']
    search_fields = ['user_id', 'entity_id']
    readonly_fields = ['timestamp']
