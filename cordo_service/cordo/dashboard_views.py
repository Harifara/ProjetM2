# coordonnateur/dashboard_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from cordo.models import ValidationCoordonnateur
from .serializers import ValidationCoordonnateurSerializer
import requests
from django.conf import settings

@api_view(['GET'])
def dashboard_coordonnateur(request):
    """
    Retourne les données pour le dashboard du coordonnateur :
    - KPI : total, approuvés, rejetés, en attente
    - Décaissements validés et en attente via l'API Finance
    """
    # 🔹 Toutes les validations existantes
    validations = ValidationCoordonnateur.objects.all()
    serializer_validations = ValidationCoordonnateurSerializer(validations, many=True)

    # 🔹 KPI
    total_validations = validations.count()
    approuvees = validations.filter(decision='approuve').count()
    rejetees = validations.filter(decision='rejete').count()

    # 🔹 IDs des décaissements déjà validés
    validated_ids = list(validations.values_list('demande_decaissement_id', flat=True))

    # 🔹 Récupération des décaissements via l'API Finance
    try:
        resp = requests.get(f"{settings.FINANCE_SERVICE_URL}/api/finance/decaissements/")
        resp.raise_for_status()
        decaissements = resp.json()
    except requests.RequestException as e:
        print(f"[Coordonnateur] Erreur récupération Finance: {e}")
        decaissements = []

    # 🔹 Filtrer les décaissements en attente
    decaissements_en_attente = [
        d for d in decaissements if d['id'] not in validated_ids
    ]
    en_attente_count = len(decaissements_en_attente)

    return Response({
        "kpi": {
            "total_validations": total_validations + en_attente_count,
            "approuvees": approuvees,
            "rejetees": rejetees,
            "en_attente": en_attente_count,
        },
        "validations": serializer_validations.data,
        "decaissements_en_attente": decaissements_en_attente
    })
