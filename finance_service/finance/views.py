from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet, DecisionDecaissementView

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet)
router.register(r'depenses', DepenseViewSet)

urlpatterns = [
    # ✅ Préfixe API pour correspondre au frontend
    path('api/finance/', include(router.urls)),
    path('api/finance/coordonnateur/decaissements/<uuid:decaissement_id>/decision/', DecisionDecaissementView.as_view())
]
