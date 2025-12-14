# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissements')
router.register(r'depenses', DepenseViewSet, basename='depenses')

urlpatterns = [
    path('api/finance/', include(router.urls)),
]
