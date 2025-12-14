from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet, DecisionDecaissementView

router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet)
router.register(r'depenses', DepenseViewSet)

urlpatterns=[
    path('', include(router.urls)),
    path('coordonnateur/decaissements/<uuid:decaissement_id>/decision/', DecisionDecaissementView.as_view())
]
