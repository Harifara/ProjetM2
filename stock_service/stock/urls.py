from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DistrictViewSet, WarehouseViewSet, StockCategoryViewSet,
    StockItemViewSet, StockMovementViewSet, InventoryCheckViewSet,
    TransferRequestViewSet, PurchaseRequestViewSet, AuditLogViewSet
)


router = DefaultRouter()
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'categories', StockCategoryViewSet, basename='category')
router.register(r'items', StockItemViewSet, basename='item')
router.register(r'movements', StockMovementViewSet, basename='movement')
router.register(r'inventory-checks', InventoryCheckViewSet, basename='inventory-check')
router.register(r'transfer-requests', TransferRequestViewSet, basename='transfer-request')
router.register(r'purchase-requests', PurchaseRequestViewSet, basename='purchase-request')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')



urlpatterns = [
    path('', include(router.urls)),
    
]
