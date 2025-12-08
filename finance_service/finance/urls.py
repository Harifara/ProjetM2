from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DemandeDecaissementItemViewSet, DepenseViewSet

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet)
router.register(r'items', DemandeDecaissementItemViewSet)
router.register(r'depenses', DepenseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
