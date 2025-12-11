# coordo/views.py
from rest_framework import viewsets
from .models import ValidationCoordonnateur
from .serializers import ValidationCoordonnateurSerializer

class ValidationCoordonnateurViewSet(viewsets.ModelViewSet):
    queryset = ValidationCoordonnateur.objects.all().order_by('-date_decision')
    serializer_class = ValidationCoordonnateurSerializer
