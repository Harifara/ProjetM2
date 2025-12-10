from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ValidationCoordinateurViewSet

router = DefaultRouter()
router.register(r'validations', ValidationCoordinateurViewSet, basename='validation-coordinateur')

urlpatterns = [
    path('', include(router.urls)),
]
