# cordo/dashboard_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ValidationCoordonnateur
from .serializers import ValidationCoordonnateurSerializer
import requests
from django.conf import settings

@api_view(['GET'])
def dashboard_coordonnateur(request):
    """
    Dashboard coordonnateur :
    - KPI : total, approuvés, rejetés, en attente
    - Décaissements en attente (récupérés via service Finance)
    """
    # 🔹 Toutes les validations existantes
    validations = ValidationCoordonnateur.objects.all()
    serializer_validations = ValidationCoordonnateurSerializer(validations, many=True)

    # 🔹 KPI
    total_validations = validations.count()
    approuvees = validations.filter(decision='approuve').count()
    rejetees = validations.filter(decision='rejete').count()

    # 🔹 Récupérer décaissements en attente depuis service Finance
    try:
        resp = requests.get(f"{settings.FINANCE_SERVICE_URL}/api/finance/decaissements/en_attente/")
        resp.raise_for_status()
        decaissements = resp.json()  # doit renvoyer une liste d'objets décaissements
    except requests.RequestException:
        decaissements = []

    en_attente_count = len(decaissements)

    # 🔹 Réponse consolidée pour le front
    return Response({
        "kpi": {
            "total": total_validations + en_attente_count,
            "approuve": approuvees,
            "rejete": rejetees,
            "en_attente": en_attente_count,
        },
        "decaissements": decaissements,
        "validations": serializer_validations.data,
    })
