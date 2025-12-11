# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissement')
router.register(r'depenses', DepenseViewSet, basename='depense')

urlpatterns = [
    path('', include(router.urls)),
]
