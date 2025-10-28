from django.contrib import admin
from .models import (
    District, Warehouse, StockCategory, StockItem, StockMovement,
    InventoryCheck, TransferRequest, PurchaseRequest, AuditLog
)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'district', 'location']
    list_filter = ['district']
    search_fields = ['name', 'location']


@admin.register(StockCategory)
class StockCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'warehouse', 'category', 'quantity', 'is_expired', 'expiry_date']
    list_filter = ['warehouse', 'category', 'is_expired']
    search_fields = ['name', 'sku', 'description']
    ordering = ['name']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock_item', 'movement_type', 'quantity', 'status', 'created_at']
    list_filter = ['movement_type', 'status', 'created_at']
    search_fields = ['stock_item__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(InventoryCheck)
class InventoryCheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'warehouse', 'checked_by', 'date']
    list_filter = ['warehouse', 'date']
    ordering = ['-date']
    readonly_fields = ['date']


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock_item', 'from_warehouse', 'to_warehouse', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'from_warehouse', 'to_warehouse', 'created_at']
    search_fields = ['stock_item__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'validated_at']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_description', 'quantity', 'department', 'status', 'created_at']
    list_filter = ['status', 'department', 'created_at']
    search_fields = ['item_description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'validated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action_type', 'user_id', 'entity_type', 'entity_id', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'entity_type', 'timestamp']
    search_fields = ['action_type', 'entity_type', 'entity_id']
    readonly_fields = ['user_id', 'action_type', 'entity_type', 'entity_id', 'timestamp', 'details', 'ip_address', 'user_agent']
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
