from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article, Stock, MouvementStock, DemandeReapprovisionnement, TransfertStock, DemandeAchat
from .serializers import ArticleSerializer, StockSerializer, DemandeReapprovisionnementSerializer, DemandeAchatSerializer

@api_view(['GET'])
def dashboard_stock(request):
    """
    API pour le dashboard de gestion de stock
    - KPI : total articles, articles en rupture, demandes en attente
    - Listes : stocks, mouvements récents, demandes réappro
    """
    # KPI
    total_articles = Article.objects.count()
    articles_rupture = Stock.objects.filter(quantite__lte=models.F('seuil_alerte')).count()
    demandes_en_attente = DemandeReapprovisionnement.objects.filter(statut='en_attente').count()
    transferts_en_attente = TransfertStock.objects.filter(statut='en_attente').count()
    demandes_achat_en_attente = DemandeAchat.objects.filter(statut='en_attente').count()

    # Données pour tableaux
    stocks = Stock.objects.select_related('article', 'magasin').all()[:50]  # limiter à 50
    demandes_reappro = DemandeReapprovisionnement.objects.select_related('article','magasin').all()[:50]
    demandes_achat = DemandeAchat.objects.select_related('article').all()[:50]

    return Response({
        "kpi": {
            "total_articles": total_articles,
            "articles_rupture": articles_rupture,
            "demandes_en_attente": demandes_en_attente,
            "transferts_en_attente": transferts_en_attente,
            "demandes_achat_en_attente": demandes_achat_en_attente,
        },
        "stocks": StockSerializer(stocks, many=True).data,
        "demandes_reappro": DemandeReapprovisionnementSerializer(demandes_reappro, many=True).data,
        "demandes_achat": DemandeAchatSerializer(demandes_achat, many=True).data,
    })
