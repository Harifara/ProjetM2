from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DecashmentRequestViewSet, DocumentViewSet, ExpenseViewSet,
    PaymentViewSet, BudgetViewSet, NotificationViewSet,
    AuditLogViewSet, health_check
)

router = DefaultRouter()
router.register(r'decashment-requests', DecashmentRequestViewSet, basename='decashment-request')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health-check'),
]
