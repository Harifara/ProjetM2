# coordonnateur/urls.py
from rest_framework.routers import DefaultRouter
from .views import ValidationCoordonnateurViewSet

router = DefaultRouter()
router.register('validations', ValidationCoordonnateurViewSet, basename='validation-coordonnateur')

urlpatterns = router.urls
