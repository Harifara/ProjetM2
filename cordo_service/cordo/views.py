from rest_framework import generics, status
from rest_framework.response import Response
from .models import ValidationCoordinateur
from .serializers import (
    ValidationCoordinateurSerializer,
    ValidationCoordinateurCreateSerializer
)

# =====================================================
# 1️⃣ Liste toutes les validations
# =====================================================
class ValidationCoordinateurListView(generics.ListAPIView):
    queryset = ValidationCoordinateur.objects.all().order_by('-date_decision')
    serializer_class = ValidationCoordinateurSerializer


# =====================================================
# 2️⃣ Détail d'une validation
# =====================================================
class ValidationCoordinateurDetailView(generics.RetrieveAPIView):
    queryset = ValidationCoordinateur.objects.all()
    serializer_class = ValidationCoordinateurSerializer
    lookup_field = 'id'


# =====================================================
# 3️⃣ Créer une nouvelle validation (POST)
# =====================================================
class ValidationCoordinateurCreateView(generics.CreateAPIView):
    queryset = ValidationCoordinateur.objects.all()
    serializer_class = ValidationCoordinateurCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            ValidationCoordinateurSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )


# =====================================================
# 4️⃣ Optionnel : lister les validations d'un décaissement
# =====================================================
class ValidationByDecaissementView(generics.ListAPIView):
    serializer_class = ValidationCoordinateurSerializer

    def get_queryset(self):
        decaissement_id = self.kwargs.get("decaissement_id")
        return ValidationCoordinateur.objects.filter(decaissement_id=decaissement_id)
