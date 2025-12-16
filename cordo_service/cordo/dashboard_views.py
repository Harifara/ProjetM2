# coordonnateur/dashboard_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from coordonnateur.models import ValidationCoordonnateur
from finance.models import Decaissement
from .serializers import ValidationCoordonnateurSerializer

@api_view(['GET'])
def dashboard_coordonnateur(request):
    """
    Retourne les données pour le dashboard du coordonnateur :
    - KPI : total, approuvés, rejetés, en attente
    - Décaissements validés
    - Décaissements en attente de validation
    """
    # 🔹 Toutes les validations existantes
    validations = ValidationCoordonnateur.objects.all()
    serializer_validations = ValidationCoordonnateurSerializer(validations, many=True)

    # 🔹 KPI
    total_validations = validations.count()
    approuvees = validations.filter(decision='approuve').count()
    rejetees = validations.filter(decision='rejete').count()

    # 🔹 Décaissements en attente : ceux qui n'ont pas de validation
    validated_ids = validations.values_list('demande_decaissement_id', flat=True)
    decaissements_en_attente = Decaissement.objects.exclude(id__in=validated_ids)
    en_attente_count = decaissements_en_attente.count()

    # 🔹 Sérialisation simple pour le frontend
    decaissements_attente_list = [
        {
            "id": d.id,
            "reference": getattr(d, "reference", ""),
            "montant_total": getattr(d, "montant_total", 0),
            "statut": getattr(d, "statut", "brouillon"),
            "date_creation": getattr(d, "date_creation", None),
            "date_decaissement": getattr(d, "date_decaissement", None)
        }
        for d in decaissements_en_attente
    ]

    return Response({
        "kpi": {
            "total_validations": total_validations + en_attente_count,
            "approuvees": approuvees,
            "rejetees": rejetees,
            "en_attente": en_attente_count,
        },
        "validations": serializer_validations.data,
        "decaissements_en_attente": decaissements_attente_list
    })
