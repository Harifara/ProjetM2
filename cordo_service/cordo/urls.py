from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ValidationCoordonnateurViewSet

router = DefaultRouter()
router.register(r'validations', ValidationCoordonnateurViewSet, basename='validation-coordonnateur')

urlpatterns = [
    path('', include(router.urls)),
]
