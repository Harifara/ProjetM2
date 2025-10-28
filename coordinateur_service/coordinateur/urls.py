from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DecashmentValidationViewSet, OperationViewViewSet, AuditLogViewSet



router = DefaultRouter()
router.register(r'validations', DecashmentValidationViewSet, basename='validation')
router.register(r'operations', OperationViewViewSet, basename='operation')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
  
]
