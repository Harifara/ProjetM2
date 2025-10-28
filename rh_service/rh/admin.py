from django.contrib import admin
from django.utils.safestring import mark_safe
from pprint import pformat
from .models import (
    District, Employee, Contract, LeaveRequest,
    Assignment, PaymentRequest, PurchaseRequest, AuditLog
)


# ============================================================
# 📍 DISTRICT
# ============================================================

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


# ============================================================
# 👨‍💼 EMPLOYE
# ============================================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'position', 'department', 'status', 'hire_date', 'district']
    list_filter = ['status', 'department', 'district']
    search_fields = ['employee_number', 'position', 'department']
    date_hierarchy = 'hire_date'
    ordering = ['employee_number']


# ============================================================
# 📄 CONTRATS
# ============================================================

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['employee', 'contract_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'contract_type']
    search_fields = ['employee__employee_number']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


# ============================================================
# 🌴 CONGÉS
# ============================================================

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__employee_number', 'reason']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


# ============================================================
# 🔄 AFFECTATIONS
# ============================================================

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'assignment_type', 'new_position', 'new_district', 'status', 'start_date']
    list_filter = ['status', 'assignment_type']
    search_fields = ['employee__employee_number', 'new_position']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


# ============================================================
# 💰 DEMANDES DE PAIEMENT
# ============================================================

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'request_type', 'amount', 'status', 'created_at']
    list_filter = ['status', 'request_type']
    search_fields = ['employee__employee_number', 'reason']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


# ============================================================
# 🛒 DEMANDES D’ACHAT
# ============================================================

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['item_description', 'quantity', 'estimated_amount', 'status', 'department', 'created_at']
    list_filter = ['status', 'department']
    search_fields = ['item_description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


# ============================================================
# 🧾 JOURNAL D’AUDIT
# ============================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['short_user', 'action_type', 'entity_type', 'short_entity', 'timestamp']
    list_filter = ['action_type', 'entity_type']
    search_fields = ['user_id', 'action_type', 'entity_id']
    date_hierarchy = 'timestamp'
    readonly_fields = [
        'user_id', 'action_type', 'entity_type', 'entity_id',
        'timestamp', 'details', 'ip_address', 'user_agent'
    ]
    ordering = ['-timestamp']

    def short_user(self, obj):
        """Affiche une version courte du user_id UUID."""
        return str(obj.user_id)[:8] + "…" if obj.user_id else "-"
    short_user.short_description = "User"

    def short_entity(self, obj):
        """Affiche une version courte de l’entity_id."""
        return str(obj.entity_id)[:8] + "…" if obj.entity_id else "-"
    short_entity.short_description = "Entity"

    def formatted_details(self, obj):
        """Affichage lisible du JSON `details`."""
        if not obj.details:
            return "-"
        return mark_safe(f"<pre>{pformat(obj.details, indent=2)}</pre>")
    formatted_details.short_description = "Détails"
