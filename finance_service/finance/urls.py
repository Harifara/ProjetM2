from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DemandeDecaissementViewSet,
    DemandeDecaissementItemViewSet,
    DepenseViewSet,
    DemandeDecaissementItemUpdateStatusView
)

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissement')
router.register(r'items', DemandeDecaissementItemViewSet, basename='decaissement-item')
router.register(r'depenses', DepenseViewSet, basename='depense')

urlpatterns = [
    path('', include(router.urls)),
    path('items/<uuid:item_id>/update-status/', DemandeDecaissementItemUpdateStatusView.as_view(), name='update-item-status'),
]
