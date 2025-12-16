# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet
from .dashboard_views import dashboard_finance

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissements')
router.register(r'depenses', DepenseViewSet, basename='depenses')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-finance/', dashboard_finance, name='dashboard-finance'),
]
